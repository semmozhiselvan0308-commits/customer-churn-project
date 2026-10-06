from fastapi import (
    FastAPI,
    Depends,
    Query,
    Header,
    HTTPException
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
import logging
import os

# =========================================================
# ML4 — LOAD REAL CHURN MODEL
# =========================================================
from phase6.predict import predict_churn as model_predict_churn


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/telecom_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Telecom Customer Intelligence API",
    version="1.0.0"
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# API KEY
# =========================================================

API_KEY = os.getenv("API_KEY", "mysecret123")


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Route not found",
            "status_code": 404
        }
    )


@app.exception_handler(401)
async def unauthorized_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.detail,
            "status_code": 401
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database unavailable",
            "status_code": 500
        }
    )


# =========================================================
# API KEY VALIDATION
# =========================================================

def verify_api_key(
    x_api_key: str | None = Header(default=None)
):
    print("AUTH CHECK - Received:", x_api_key)

    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="API key is required"
        )

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return x_api_key


# =========================================================
# PYDANTIC MODELS
# =========================================================

# -------------------------
# API1 Response Model
# -------------------------

class CustomerResponse(BaseModel):
    customer_id: str
    tenure: int
    contract_type: str
    internet_service: str
    monthly_charges: float
    churn: int


# -------------------------
# API4 Model
# -------------------------

class CustomerFeatures(BaseModel):
    service_count: int
    tenure_bucket: str
    high_charge_flag: int
    is_long_term_customer: int
    has_streaming_bundle: int
    auto_pay_flag: int
    monthly_charges: float
    total_charges: float


# -------------------------
# API5 / ML4 Request Model
# -------------------------

class ChurnPredictionRequest(BaseModel):
    tenure: int = Field(..., ge=0, le=100)
    monthly_charges: float = Field(..., gt=0)
    contract_type: str
    service_count: int


# -------------------------
# Error Response Model
# -------------------------

class ErrorResponse(BaseModel):
    detail: str
    status_code: int


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# SERVICE LAYER — CHURN SUMMARY
# =========================================================

def get_churn_summary(db: Session):

    try:

        # 1. Total customers
        total_customers = db.execute(
            text("""
                SELECT COUNT(DISTINCT customer_id)
                FROM fact_customer_account
            """)
        ).scalar()

        # 2. Total churned customers
        churned = db.execute(
            text("""
                SELECT COUNT(DISTINCT customer_id)
                FROM fact_customer_account
                WHERE churn = 1
            """)
        ).scalar()

        # 3. Overall churn rate
        churn_rate = (
            churned / total_customers
            if total_customers > 0
            else 0
        )

        # 4. Churn rate by contract type
        contract_rows = db.execute(
            text("""
                SELECT
                    dc.contract_name,
                    AVG(fca.churn) AS churn_rate
                FROM fact_customer_account fca
                JOIN dim_contract dc
                    ON fca.contract_id = dc.contract_id
                GROUP BY dc.contract_name
            """)
        ).fetchall()

        by_contract = [
            {
                "contract_type": row.contract_name,
                "churn_rate": round(float(row.churn_rate), 4)
            }
            for row in contract_rows
        ]

        # 5. Churn rate by internet service
        internet_rows = db.execute(
            text("""
                SELECT
                    internet_service,
                    AVG(churn) AS churn_rate
                FROM fact_customer_account
                GROUP BY internet_service
            """)
        ).fetchall()

        by_internet_service = [
            {
                "internet_service": row.internet_service,
                "churn_rate": round(float(row.churn_rate), 4)
            }
            for row in internet_rows
        ]

        # 6. Final structured response
        return {
            "total_customers": total_customers,
            "churned": churned,
            "churn_rate": round(churn_rate, 4),
            "by_contract": by_contract,
            "by_internet_service": by_internet_service
        }

    except Exception:

        logger.error(
            "Database error in get_churn_summary"
        )

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )


# =========================================================
# API 1 — CUSTOMER PROFILE
# =========================================================

@app.get(
    "/customer/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            c.customer_id,
            f.tenure,
            dc.contract_name AS contract_type,
            f.internet_service,
            f.monthly_charges,
            f.churn
        FROM customers c
        JOIN fact_customer_account f
            ON c.customer_id = f.customer_id
        JOIN dim_contract dc
            ON f.contract_id = dc.contract_id
        WHERE c.customer_id = :customer_id
    """)

    try:

        result = db.execute(
            query,
            {"customer_id": customer_id}
        ).mappings().first()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        return result

    finally:
        db.close()


# =========================================================
# API 2 — CHURN SUMMARY
# =========================================================

@app.get("/churn/summary")
def churn_summary(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):

    logger.info(
        "Request: GET /churn/summary"
    )

    result = get_churn_summary(db)

    logger.info(
        "Response: GET /churn/summary - 200"
    )

    return result


# =========================================================
# API 3 — HIGH-RISK CUSTOMERS
# =========================================================

@app.get("/customers/high-risk")
def high_risk_customers(
    limit: int = Query(50, ge=1),
    min_tenure: int | None = Query(None, ge=0),
    max_tenure: int | None = Query(None, ge=0),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):

    logger.info(
        f"Request: GET /customers/high-risk "
        f"limit={limit}, "
        f"min_tenure={min_tenure}, "
        f"max_tenure={max_tenure}"
    )

    try:

        query = """
            SELECT
                customer_id,
                tenure,
                monthly_charges,
                contract,
                risk_reason
            FROM v_high_risk_customers
            WHERE 1=1
        """

        params = {}

        if min_tenure is not None:
            query += " AND tenure >= :min_tenure"
            params["min_tenure"] = min_tenure

        if max_tenure is not None:
            query += " AND tenure <= :max_tenure"
            params["max_tenure"] = max_tenure

        query += " ORDER BY monthly_charges DESC LIMIT :limit"

        params["limit"] = limit

        rows = db.execute(
            text(query),
            params
        ).fetchall()

        logger.info(
            "Response: GET /customers/high-risk - 200"
        )

        return [
            {
                "customer_id": row.customer_id,
                "tenure": row.tenure,
                "monthly_charges": float(row.monthly_charges),
                "contract": row.contract,
                "risk_reason": row.risk_reason
            }
            for row in rows
        ]

    except Exception:

        logger.error(
            "Database error in /customers/high-risk"
        )

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )


# =========================================================
# API 4 — CUSTOMER FEATURES
# =========================================================

@app.get(
    "/customer/{customer_id}/features",
    response_model=CustomerFeatures
)
def get_customer_features(
    customer_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):

    logger.info(
        f"Request: GET /customer/{customer_id}/features"
    )

    try:

        row = db.execute(
            text("""
                SELECT
                    service_count,
                    tenure_bucket,
                    high_charge_flag,
                    is_long_term_customer,
                    has_streaming_bundle,
                    auto_pay_flag,
                    monthly_charges,
                    total_charges
                FROM customer_ml_features
                WHERE customer_id = :customer_id
            """),
            {
                "customer_id": customer_id
            }
        ).fetchone()

        if row is None:

            logger.info(
                f"Response: GET "
                f"/customer/{customer_id}/features - 404"
            )

            return JSONResponse(
                status_code=404,
                content={
                    "detail": "Customer not found",
                    "status_code": 404
                }
            )

        logger.info(
            f"Response: GET "
            f"/customer/{customer_id}/features - 200"
        )

        return {
            "service_count": row.service_count,
            "tenure_bucket": row.tenure_bucket,
            "high_charge_flag": row.high_charge_flag,
            "is_long_term_customer": row.is_long_term_customer,
            "has_streaming_bundle": row.has_streaming_bundle,
            "auto_pay_flag": row.auto_pay_flag,
            "monthly_charges": float(row.monthly_charges),
            "total_charges": float(row.total_charges)
        }

    except Exception:

        logger.error(
            f"Response: GET "
            f"/customer/{customer_id}/features - 500"
        )

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )


# =========================================================
# API 5 + ML4 — REAL CHURN PREDICTION
# =========================================================

@app.post("/predict-churn")
def predict_churn(
    request: ChurnPredictionRequest,
    api_key: str = Depends(verify_api_key)
):

    logger.info(
        f"Request: POST /predict-churn "
        f"tenure={request.tenure}, "
        f"monthly_charges={request.monthly_charges}, "
        f"contract_type={request.contract_type}, "
        f"service_count={request.service_count}"
    )

    try:

        # Call the real trained ML model
        result = model_predict_churn(
            tenure=request.tenure,
            monthly_charges=request.monthly_charges,
            contract_type=request.contract_type,
            service_count=request.service_count
        )

        logger.info(
            f"ML Prediction: {result}"
        )

        logger.info(
            "Response: POST /predict-churn - 200"
        )

        return result

    except Exception as e:

        logger.error(
            f"Model prediction error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Model prediction failed"
        )


# =========================================================
# END OF PHASE 6 API
# =========================================================
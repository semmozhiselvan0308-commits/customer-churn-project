import React, { useState } from "react";
import axios from "axios";

function CustomerSearch() {
  const [customerId, setCustomerId] = useState("");

  const [customer, setCustomer] = useState(null);
  const [churnSummary, setChurnSummary] = useState(null);
  const [highRisk, setHighRisk] = useState(null);
  const [features, setFeatures] = useState(null);
  const [prediction, setPrediction] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_KEY = "mysecret123";

  const handleSearch = async () => {
    if (!customerId.trim()) {
      setError("Please enter a customer ID");
      return;
    }

    setLoading(true);
    setError("");

    setCustomer(null);
    setChurnSummary(null);
    setHighRisk(null);
    setFeatures(null);
    setPrediction(null);

    try {
      // ==========================================
      // API 1 - Customer Profile
      // PORT 8000
      // ==========================================

      const customerResponse = await axios.get(
        `http://127.0.0.1:8000/customer/${customerId}`
      );

      const customerData = customerResponse.data;

      setCustomer(customerData);


      // ==========================================
      // API 2 - Churn Summary
      // PORT 8000
      // ==========================================

      const churnResponse = await axios.get(
        "http://127.0.0.1:8000/churn/summary",
        {
          headers: {
            "x-api-key": API_KEY,
          },
        }
      );

      setChurnSummary(churnResponse.data);


      // ==========================================
      // API 3 - High Risk Customers
      // PORT 8000
      // ==========================================

      const riskResponse = await axios.get(
        "http://127.0.0.1:8000/customers/high-risk",
        {
          headers: {
            "x-api-key": API_KEY,
          },
        }
      );

      setHighRisk(riskResponse.data);


      // ==========================================
      // API 4 - Customer Features
      // PORT 8000
      // ==========================================

      const featuresResponse = await axios.get(
        `http://127.0.0.1:8000/customer/${customerId}/features`,
        {
          headers: {
            "x-api-key": API_KEY,
          },
        }
      );

      const featuresData = featuresResponse.data;

      setFeatures(featuresData);


      // ==========================================
      // API 5 - Predict Churn
      // PORT 8000
      //
      // API5 requires:
      // tenure
      // monthly_charges
      // contract_type
      // service_count
      // ==========================================

      const predictionResponse = await axios.post(
        "http://127.0.0.1:8000/predict-churn",
        {
          tenure: customerData.tenure,
          monthly_charges: customerData.monthly_charges,
          contract_type: customerData.contract_type,
          service_count: featuresData.service_count,
        },
        {
          headers: {
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
          },
        }
      );

      setPrediction(predictionResponse.data);

    } catch (e) {
      console.error("API ERROR:", e);

      console.error("URL:", e.config?.url);
      console.error("STATUS:", e.response?.status);
      console.error("RESPONSE:", e.response?.data);

      if (e.response?.status === 404) {
        setError(
          `Endpoint not found: ${e.config?.url}`
        );
      } else if (e.response?.status === 401) {
        setError(
          "Authentication failed. Please check the API key."
        );
      } else if (e.response?.status === 422) {
        setError(
          `Invalid request: ${
            JSON.stringify(
              e.response?.data?.detail
            )
          }`
        );
      } else if (e.response?.status === 500) {
        setError(
          e.response?.data?.detail ||
          "Server error occurred."
        );
      } else {
        setError(
          "Something went wrong. Please check that the FastAPI server is running."
        );
      }

    } finally {
      setLoading(false);
    }
  };


  return (
    <div
      style={{
        padding: "30px",
        fontFamily: "Arial",
        maxWidth: "1000px",
        margin: "auto",
      }}
    >

      <h1>Customer Intelligence Dashboard</h1>


      {/* ==========================================
          SEARCH
      ========================================== */}

      <div style={{ marginBottom: "30px" }}>

        <input
          type="text"
          placeholder="Enter Customer ID"
          value={customerId}
          onChange={(e) =>
            setCustomerId(e.target.value)
          }
          style={{
            padding: "10px",
            width: "250px",
          }}
        />

        <button
          onClick={handleSearch}
          style={{
            marginLeft: "10px",
            padding: "10px 20px",
            cursor: "pointer",
          }}
        >
          Search
        </button>

      </div>


      {/* ==========================================
          LOADING
      ========================================== */}

      {loading && (
        <p
          style={{
            fontWeight: "bold",
          }}
        >
          Loading customer intelligence...
        </p>
      )}


      {/* ==========================================
          ERROR
      ========================================== */}

      {error && (
        <div
          style={{
            marginTop: "15px",
            marginBottom: "20px",
            padding: "15px",
            border: "1px solid red",
            borderRadius: "8px",
            backgroundColor: "#ffe6e6",
            color: "red",
            fontWeight: "bold",
          }}
        >
          {error}
        </div>
      )}


      {/* ==========================================
          API 1 - CUSTOMER PROFILE
      ========================================== */}

      {customer && (
        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "10px",
          }}
        >

          <h2>1. Customer Profile</h2>

          <p>
            <strong>Customer ID:</strong>{" "}
            {customer.customer_id}
          </p>

          <p>
            <strong>Tenure:</strong>{" "}
            {customer.tenure}
          </p>

          <p>
            <strong>Contract Type:</strong>{" "}
            {customer.contract_type}
          </p>

          <p>
            <strong>Internet Service:</strong>{" "}
            {customer.internet_service}
          </p>

          <p>
            <strong>Monthly Charges:</strong>{" "}
            {customer.monthly_charges}
          </p>

          <p
            style={{
              backgroundColor:
                Number(customer.churn) === 1
                  ? "red"
                  : "green",
              color: "white",
              padding: "10px",
              borderRadius: "5px",
              fontWeight: "bold",
            }}
          >
            Churn Status:{" "}
            {Number(customer.churn) === 1
              ? "Churned"
              : "Active"}
          </p>

        </div>
      )}


      {/* ==========================================
          API 2 - CHURN SUMMARY
      ========================================== */}

      {churnSummary && (
        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "10px",
          }}
        >

          <h2>2. Churn Summary</h2>

          <p>
            <strong>Total Customers:</strong>{" "}
            {churnSummary.total_customers ?? "N/A"}
          </p>

          <p>
            <strong>Total Churned:</strong>{" "}
            {churnSummary.churned ??
              churnSummary.total_churned ??
              churnSummary.churned_customers ??
              "N/A"}
          </p>

          <p>
            <strong>Overall Churn Rate:</strong>{" "}
            {churnSummary.churn_rate !== undefined
              ? (
                  Number(churnSummary.churn_rate) * 100
                ).toFixed(2)
              : "N/A"}
            %
          </p>


          <h3>Churn by Contract</h3>

          {Array.isArray(churnSummary.by_contract) ? (

            churnSummary.by_contract.length > 0 ? (

              churnSummary.by_contract.map(
                (item, index) => (

                  <p
                    key={
                      item.contract_type || index
                    }
                  >
                    <strong>
                      {item.contract_type}:
                    </strong>{" "}
                    {(
                      Number(item.churn_rate) * 100
                    ).toFixed(2)}
                    %
                  </p>

                )
              )

            ) : (

              <p>
                Contract churn data not available.
              </p>

            )

          ) : (

            <p>
              Contract churn data not available.
            </p>

          )}


          <h3>Churn by Internet Service</h3>

          {Array.isArray(
            churnSummary.by_internet_service
          ) ? (

            churnSummary.by_internet_service.length > 0 ? (

              churnSummary.by_internet_service.map(
                (item, index) => (

                  <p
                    key={
                      item.internet_service || index
                    }
                  >
                    <strong>
                      {item.internet_service}:
                    </strong>{" "}
                    {(
                      Number(item.churn_rate) * 100
                    ).toFixed(2)}
                    %
                  </p>

                )
              )

            ) : (

              <p>
                Internet service churn data not available.
              </p>

            )

          ) : (

            <p>
              Internet service churn data not available.
            </p>

          )}

        </div>
      )}


      {/* ==========================================
          API 3 - HIGH RISK CUSTOMERS
      ========================================== */}

      {highRisk && (
        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "10px",
          }}
        >

          <h2>3. High-Risk Customers</h2>

          {Array.isArray(highRisk) ? (

            highRisk.length > 0 ? (

              highRisk.map((item, index) => (

                <div
                  key={index}
                  style={{
                    padding: "10px",
                    marginBottom: "10px",
                    border: "1px solid #ddd",
                    borderRadius: "5px",
                  }}
                >

                  <p>
                    <strong>Customer ID:</strong>{" "}
                    {item.customer_id}
                  </p>

                  <p>
                    <strong>Tenure:</strong>{" "}
                    {item.tenure}
                  </p>

                  <p>
                    <strong>Monthly Charges:</strong>{" "}
                    {item.monthly_charges}
                  </p>

                  <p>
                    <strong>Contract:</strong>{" "}
                    {item.contract}
                  </p>

                  <p>
                    <strong>Risk Reason:</strong>{" "}
                    {item.risk_reason}
                  </p>

                </div>

              ))

            ) : (

              <p>
                No high-risk customers found.
              </p>

            )

          ) : (

            <pre>
              {JSON.stringify(
                highRisk,
                null,
                2
              )}
            </pre>

          )}

        </div>
      )}


      {/* ==========================================
          API 4 - CUSTOMER FEATURES
      ========================================== */}

      {features && (
        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "10px",
          }}
        >

          <h2>4. Customer Features</h2>

          <pre
            style={{
              backgroundColor: "#f5f5f5",
              padding: "15px",
              borderRadius: "5px",
              overflowX: "auto",
            }}
          >
            {JSON.stringify(
              features,
              null,
              2
            )}
          </pre>

        </div>
      )}


      {/* ==========================================
          API 5 - CHURN PREDICTION
      ========================================== */}

      {prediction && (
        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "10px",
          }}
        >

          <h2>5. Churn Prediction</h2>

          <pre
            style={{
              backgroundColor: "#f5f5f5",
              padding: "15px",
              borderRadius: "5px",
              overflowX: "auto",
            }}
          >
            {JSON.stringify(
              prediction,
              null,
              2
            )}
          </pre>

        </div>
      )}

    </div>
  );
}

export default CustomerSearch;
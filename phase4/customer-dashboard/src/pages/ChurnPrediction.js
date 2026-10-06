import React, { useState } from "react";
import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "X-API-Key": "mysecret123",
  },
});

function ChurnPrediction() {
  const [formData, setFormData] = useState({
    tenure: "",
    monthly_charges: "",
    contract_type: "Month-to-month",
    service_count: "",
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await API.post("/predict-churn", {
        tenure: Number(formData.tenure),
        monthly_charges: Number(formData.monthly_charges),
        contract_type: formData.contract_type,
        service_count: Number(formData.service_count),
      });

      setResult(response.data);
    } catch (e) {
      if (e.response?.status === 422) {
        setError(JSON.stringify(e.response.data.detail));
      } else {
        setError("Unable to get churn prediction.");
      }
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score) => {
    if (score < 0.3) {
      return "green";
    } else if (score <= 0.6) {
      return "orange";
    } else {
      return "red";
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>Churn Prediction</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Tenure</label>
          <br />
          <input
            type="number"
            name="tenure"
            value={formData.tenure}
            onChange={handleChange}
            min="0"
            required
          />
        </div>

        <br />

        <div>
          <label>Monthly Charges</label>
          <br />
          <input
            type="number"
            name="monthly_charges"
            value={formData.monthly_charges}
            onChange={handleChange}
            min="0"
            step="0.01"
            required
          />
        </div>

        <br />

        <div>
          <label>Contract Type</label>
          <br />

          <select
            name="contract_type"
            value={formData.contract_type}
            onChange={handleChange}
          >
            <option value="Month-to-month">Month-to-month</option>
            <option value="One year">One year</option>
            <option value="Two year">Two year</option>
          </select>
        </div>

        <br />

        <div>
          <label>Service Count</label>
          <br />
          <input
            type="number"
            name="service_count"
            value={formData.service_count}
            onChange={handleChange}
            min="0"
            max="8"
            required
          />
        </div>

        <br />

        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict Churn"}
        </button>
      </form>

      {error && (
        <div style={{ color: "red", marginTop: "20px" }}>
          <strong>Error:</strong>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div style={{ marginTop: "30px" }}>
          <h2>Prediction Result</h2>

          <div
            style={{
              padding: "20px",
              border: `4px solid ${getRiskColor(result.risk_score)}`,
              borderRadius: "10px",
              width: "300px",
            }}
          >
            <h3
              style={{
                color: getRiskColor(result.risk_score),
              }}
            >
              Risk Score: {(result.risk_score * 100).toFixed(1)}%
            </h3>

            <p>
              <strong>Prediction:</strong> {result.prediction}
            </p>

            <p>
              <strong>Confidence:</strong>{" "}
              {(result.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChurnPrediction;
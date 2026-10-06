import React, { useEffect, useState } from "react";
import { getChurnSummary } from "../api";


function ChurnSummary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
  getChurnSummary()
    .then((response) => {
      setData(response.data);
      setLoading(false);
    })
    .catch((err) => {
      console.error("Churn summary error:", err);
      setError("Failed to fetch churn summary");
      setLoading(false);
    });
}, []);

  if (loading) {
    return <h2>Loading churn summary...</h2>;
  }

  if (error) {
    return <h2>Error: {error}</h2>;
  }

  const {
    total_customers,
    churned,
    churn_rate,
    by_contract,
  } = data;

  return (
    <div style={{ padding: "30px" }}>
      <h1>Churn Analytics</h1>

      <p>
        This page shows the key customer churn metrics and churn rates by
        contract type.
      </p>

      {/* Metric Cards */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "25px",
          marginBottom: "30px",
        }}
      >
        <div
          style={{
            border: "1px solid #ddd",
            padding: "20px",
            borderRadius: "10px",
            minWidth: "180px",
          }}
        >
          <h3>Total Customers</h3>
          <h2>{total_customers}</h2>
        </div>

        <div
          style={{
            border: "1px solid #ddd",
            padding: "20px",
            borderRadius: "10px",
            minWidth: "180px",
          }}
        >
          <h3>Total Churned</h3>
          <h2>{churned}</h2>
        </div>

        <div
          style={{
            border: "1px solid #ddd",
            padding: "20px",
            borderRadius: "10px",
            minWidth: "180px",
          }}
        >
          <h3>Churn Rate</h3>
          <h2>{(churn_rate * 100).toFixed(1)}%</h2>
        </div>
      </div>

      {/* Contract Churn Table */}
      <h2>Churn Rate by Contract Type</h2>

      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          maxWidth: "800px",
          marginTop: "15px",
        }}
      >
        <thead>
          <tr>
            <th
              style={{
                border: "1px solid #ddd",
                padding: "12px",
                textAlign: "left",
              }}
            >
              Contract Type
            </th>

            <th
              style={{
                border: "1px solid #ddd",
                padding: "12px",
                textAlign: "left",
              }}
            >
              Churn Rate
            </th>

            <th
              style={{
                border: "1px solid #ddd",
                padding: "12px",
                textAlign: "left",
              }}
            >
              Visual
            </th>
          </tr>
        </thead>

        <tbody>
          {by_contract.map((item) => (
            <tr key={item.contract_type}>
              <td
                style={{
                  border: "1px solid #ddd",
                  padding: "12px",
                }}
              >
                {item.contract_type}
              </td>

              <td
                style={{
                  border: "1px solid #ddd",
                  padding: "12px",
                }}
              >
                {(item.churn_rate * 100).toFixed(1)}%
              </td>

              <td
                style={{
                  border: "1px solid #ddd",
                  padding: "12px",
                }}
              >
                <div
                  style={{
                    width: `${item.churn_rate * 300}px`,
                    height: "20px",
                    backgroundColor: "steelblue",
                    borderRadius: "5px",
                  }}
                ></div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ChurnSummary;
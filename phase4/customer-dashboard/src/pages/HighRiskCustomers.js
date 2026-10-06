import React, { useEffect, useState } from "react";
import API from "../api";

function HighRiskCustomers() {
  const [customers, setCustomers] = useState([]);
  const [limit, setLimit] = useState(50);
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    const fetchHighRiskCustomers = async () => {
      try {
        const response = await API.get(
          `/customers/high-risk?limit=${limit}`
        );

        setCustomers(response.data);
      } catch (error) {
        console.error("Error fetching high-risk customers:", error);
        setCustomers([]);
      }
    };

    fetchHighRiskCustomers();
  }, [limit]);

  const sortedCustomers = [...customers].sort((a, b) => {
    return sortAsc
      ? a.tenure - b.tenure
      : b.tenure - a.tenure;
  });

  const handleSort = () => {
    setSortAsc(!sortAsc);
  };

  const handleLoadMore = () => {
    setLimit(limit + 50);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>High-Risk Customers</h1>

      <div
        style={{
          padding: "15px",
          marginBottom: "20px",
          backgroundColor: "#f5f5f5",
          borderRadius: "8px",
          fontSize: "18px",
          fontWeight: "bold",
        }}
      >
        {customers.length} high-risk customers identified
      </div>

      {customers.length === 0 ? (
        <p>No high-risk customers found</p>
      ) : (
        <>
          <table
            border="1"
            cellPadding="10"
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr>
                <th>Customer ID</th>

                <th
                  onClick={handleSort}
                  style={{ cursor: "pointer" }}
                >
                  Tenure {sortAsc ? "↑" : "↓"}
                </th>

                <th>Monthly Charges</th>
                <th>Contract </th>
                <th>Risk Reason</th>
              </tr>
            </thead>

            <tbody>
              {sortedCustomers.map((customer) => (
                <tr key={customer.customer_id}>
                  <td>{customer.customer_id}</td>
                  <td>{customer.tenure}</td>
                  <td>
                    ${Number(customer.monthly_charges).toFixed(2)}
                  </td>
                  <td>{customer.contract}</td>
                  <td>{customer.risk_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <button
            onClick={handleLoadMore}
            style={{
              marginTop: "20px",
              padding: "10px 20px",
              cursor: "pointer",
            }}
          >
            Load More
          </button>
        </>
      )}
    </div>
  );
}

export default HighRiskCustomers;
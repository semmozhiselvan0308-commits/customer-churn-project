import React, { useState } from "react";

import CustomerSearch from "./pages/CustomerSearch";
import ChurnSummary from "./pages/ChurnSummary";
import HighRiskCustomers from "./pages/HighRiskCustomers";
import ChurnPrediction from "./pages/ChurnPrediction";

import "./App.css";

function App() {
  const [activeSection, setActiveSection] = useState("search");

  return (
    <div className="dashboard">

      {/* HEADER */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>📊 Customer Churn Intelligence</h1>
          <p>
            Telecom Customer Analytics & Machine Learning Dashboard
          </p>
        </div>
      </header>

      {/* NAVIGATION */}
      <nav className="dashboard-nav">

        <button
          className={`nav-btn ${
            activeSection === "search" ? "active" : ""
          }`}
          onClick={() => setActiveSection("search")}
        >
          🔍 Customer Search
        </button>

        <button
          className={`nav-btn ${
            activeSection === "analytics" ? "active" : ""
          }`}
          onClick={() => setActiveSection("analytics")}
        >
          📈 Churn Analytics
        </button>

        <button
          className={`nav-btn ${
            activeSection === "risk" ? "active" : ""
          }`}
          onClick={() => setActiveSection("risk")}
        >
          ⚠️ High-Risk Customers
        </button>

        <button
          className={`nav-btn ${
            activeSection === "prediction" ? "active" : ""
          }`}
          onClick={() => setActiveSection("prediction")}
        >
          🤖 Churn Prediction
        </button>

      </nav>

      {/* CONTENT */}
      <main className="dashboard-content">

        {activeSection === "search" && (
          <section className="section-card">

            <div className="section-heading">
              <div className="section-icon">🔍</div>

              <div>
                <h2>Customer Search</h2>
                <p>
                  Search for a customer and view their details.
                </p>
              </div>
            </div>

            <div className="section-body">
              <CustomerSearch />
            </div>

          </section>
        )}

        {activeSection === "analytics" && (
          <section className="section-card">

            <div className="section-heading">
              <div className="section-icon">📈</div>

              <div>
                <h2>Churn Analytics</h2>
                <p>
                  View overall churn statistics and contract-wise
                  churn rates.
                </p>
              </div>
            </div>

            <div className="section-body">
              <ChurnSummary />
            </div>

          </section>
        )}

        {activeSection === "risk" && (
          <section className="section-card">

            <div className="section-heading">
              <div className="section-icon">⚠️</div>

              <div>
                <h2>High-Risk Customers</h2>
                <p>
                  Identify customers who require retention attention.
                </p>
              </div>
            </div>

            <div className="section-body">
              <HighRiskCustomers />
            </div>

          </section>
        )}

        {activeSection === "prediction" && (
          <section className="section-card">

            <div className="section-heading">
              <div className="section-icon">🤖</div>

              <div>
                <h2>Churn Prediction</h2>
                <p>
                  Use the machine learning model to predict customer
                  churn risk.
                </p>
              </div>
            </div>

            <div className="section-body">
              <ChurnPrediction />
            </div>

          </section>
        )}

      </main>

      {/* FOOTER */}
      <footer className="dashboard-footer">
        <p>Customer Churn Prediction System</p>
        <span>React • FastAPI • Machine Learning</span>
      </footer>

    </div>
  );
}

export default App;
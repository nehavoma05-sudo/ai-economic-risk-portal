import { useEffect, useState } from "react";
import { API_BASE_URL } from "./config";
import "./App.css";

function App() {
  const [commodities, setCommodities] = useState(null);
  const [overview, setOverview] = useState([]);
  const [activePanel, setActivePanel] = useState(null);

  const [warScore, setWarScore] = useState("");
  const [shippingScore, setShippingScore] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [crashWarning, setCrashWarning] = useState(null);
  const [budgetInput, setBudgetInput] = useState({
    monthly_budget: "",
    petrol_liters: "",
    diesel_liters: "",
    lpg_cylinders: "",
    groceries_cost: "",
    electricity_cost: "",
    medical_cost: "",
  });
  const [budgetResult, setBudgetResult] = useState(null);
  const [liveRiskNews, setLiveRiskNews] = useState(null);

  async function fetchCommodities() {
    const res = await fetch(`${API_BASE_URL}/commodities`);
    const data = await res.json();
    setCommodities(data);
  }

  async function fetchEconomicOverview() {
    const res = await fetch(`${API_BASE_URL}/economic-overview`);
    const data = await res.json();
    setOverview(data);
  }

  async function predictImpact() {
    const res = await fetch(`${API_BASE_URL}/predict-economic-impact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        war_score: Number(warScore),
        shipping_score: Number(shippingScore),
      }),
    });

    const data = await res.json();
    setPrediction(data);
  }

  async function fetchCrashWarning() {
    const res = await fetch(`${API_BASE_URL}/stock-crash-warning`);
    const data = await res.json();
    setCrashWarning(data);
  }

  async function predictBudget() {
  try {
    const res = await fetch(`${API_BASE_URL}/budget-prediction`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        monthly_budget: Number(budgetInput.monthly_budget),
        petrol_liters: Number(budgetInput.petrol_liters),
        diesel_liters: Number(budgetInput.diesel_liters),
        lpg_cylinders: Number(budgetInput.lpg_cylinders),
        groceries_cost: Number(budgetInput.groceries_cost),
        electricity_cost: Number(budgetInput.electricity_cost),
        medical_cost: Number(budgetInput.medical_cost),
      }),
    });
    const data = await res.json();
    setBudgetResult(data);
  } catch (err) {
    console.log("Budget prediction error:", err);
  }
}

async function fetchLiveRiskNews() {
  try {
    const res = await fetch(`${API_BASE_URL}/live-dashboard`);
    const data = await res.json();
    setLiveRiskNews(data);
  } catch (err) {
    console.log("Live risk news error:", err);
  }
}

  useEffect(() => {
    fetchCommodities();
    fetchEconomicOverview();
    fetchCrashWarning();

    const interval = setInterval(() => {
      fetchCommodities();
      fetchEconomicOverview();
      fetchCrashWarning();
    }, 15 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <main className="page">
        <section className="left-section">
          <div className="section-header">
            <h2>Live Commodity Indicators</h2>
            <button onClick={fetchCommodities}>Refresh</button>
          </div>

          {commodities && (
            <>
              <p className="updated-time">Last updated: {commodities.timestamp}</p>

              <div className="card-grid">
                {Object.entries(commodities)
                  .filter(([key]) => key !== "timestamp")
                  .map(([key, item]) => (
                    <div className="info-card" key={key}>
                      <p>{key.replaceAll("_", " ").toUpperCase()}</p>
                      <h3>
                        {item.price}
                        <span className={item.market_direction === "UP" ? "green" : "red"}>
                          {" "}
                          {item.change_percent}%
                        </span>
                      </h3>
                      <small>Previous Close: {item.previous_close}</small>
                    </div>
                  ))}
              </div>
            </>
          )}

          <div className="section-header">
            <h2>Economic Overview</h2>
            <button onClick={fetchEconomicOverview}>Refresh</button>
          </div>

          {overview.length > 0 && (
            <div className="card-grid">
              {overview.map((item) => (
                <div className="info-card" key={item.symbol}>
                  <p>{item.name}</p>
                  <h3>
                    {item.current_value}
                    <span className={item.daily_change_percent >= 0 ? "green" : "red"}>
                      {" "}
                      {item.daily_change_percent}%
                    </span>
                  </h3>
                  <small>
                    7D: {item.seven_day_change_percent}% | 30D:{" "}
                    {item.thirty_day_change_percent}%
                  </small>
                </div>
              ))}
            </div>
          )}
        </section>

        <aside className="right-section">
          <div className="action-panel">
            <h2>AI Prediction Tools</h2>
            <p>Choose one feature to analyze your economic risk.</p>

            <button className="action-btn" onClick={() => setActivePanel("economic")}>
              Predict Economic Impact
            </button>

            <button
              className="action-btn"
              onClick={() => {
                setActivePanel("crash");
                fetchCrashWarning();
              }}
            >
              Stock Crash Warning
            </button>

            <button className="action-btn" onClick={() => setActivePanel("budget")}>
              Budget Prediction
            </button>

            <button className="action-btn" onClick={() => { setActivePanel("liveRiskNews");fetchLiveRiskNews();}}>
              Live Risk News
            </button>
          </div>
        </aside>
      </main>

      {activePanel && <div className="overlay" onClick={() => setActivePanel(null)} />}

      {activePanel === "economic" && (
        <div className="slide-panel">
          <div className="panel-header">
            <h2>Economic Impact Predictor</h2>
            <button onClick={() => setActivePanel(null)}>✕</button>
          </div>

          <div className="rules-box">
            <p>Score Rules</p>
            <span>0 - 0.3 = Low</span>
            <span>0.3 - 0.6 = Medium</span>
            <span>0.6 - 1 = High</span>
          </div>

          <div className="input-group">
            <label>War Score</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={warScore}
              onChange={(e) => setWarScore(e.target.value)}
              placeholder="Enter war score"
            />
          </div>

          <div className="input-group">
            <label>Shipping Score</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={shippingScore}
              onChange={(e) => setShippingScore(e.target.value)}
              placeholder="Enter shipping score"
            />
          </div>

          <button className="predict-btn" onClick={predictImpact}>
            Predict
          </button>

          {prediction && (
            <div className="prediction-results">
              <div className="result-card"><h4>Petrol Rise</h4><p>₹{prediction.petrol_rise}/L</p></div>
              <div className="result-card"><h4>Diesel Rise</h4><p>₹{prediction.diesel_rise}/L</p></div>
              <div className="result-card"><h4>LPG Rise</h4><p>₹{prediction.lpg_rise}/Cylinder</p></div>
              <div className="result-card"><h4>Rupee Change</h4><p>{prediction.rupee_change}</p></div>
              <div className="result-card"><h4>Inflation</h4><p>{prediction.inflation}%</p></div>
            </div>
          )}
        </div>
      )}

      {activePanel === "crash" && (
        <div className="slide-panel">
          <div className="panel-header">
            <h2>Stock Crash Warning</h2>

            <div>
              <button className="refresh-btn" onClick={fetchCrashWarning}>
                Refresh
              </button>
              <button onClick={() => setActivePanel(null)}>✕</button>
            </div>
          </div>

          {crashWarning ? (
            <div className="crash-warning-box">
              <p className="crash-updated-time">Last updated: {crashWarning.timestamp}
              </p>
              
              <div className="result-card">
              <h4>Crash Probability</h4>
              <p>
                {crashWarning.crash_probability !== undefined
                  ? `${(crashWarning.crash_probability * 100).toFixed(2)}%`
                  : "N/A"}
              </p>
            </div>

            <div className="result-card">
              <h4>Risk Level</h4>
              <p className={`risk-${crashWarning.crash_risk_level?.toLowerCase() || "unknown"}`}>
                {crashWarning.crash_risk_level || "UNKNOWN"}
              </p>
            </div>

              <div className="result-card">
                <h4>Market Alert</h4>
                <p>{crashWarning.market_alert}</p>
              </div>

              <div className="result-card">
                <h4>Reasons</h4>
                {crashWarning.reason?.length > 0 ? (
                  <ul>
                    {crashWarning.reason.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No major risk reasons detected.</p>
                )}
              </div>
            </div>
          ) : (
            <p>Loading crash warning...</p>
          )}
        </div>
      )}

      {activePanel === "budget" && (
  <div className="slide-panel">
    <div className="panel-header">
      <h2>Budget Prediction</h2>
      <button onClick={() => setActivePanel(null)}>✕</button>
    </div>

    <div className="budget-form-grid">
      <div className="input-group">
        <label>Monthly Budget</label>
        <input
          type="number"
          value={budgetInput.monthly_budget}
          onChange={(e) =>
            setBudgetInput({
              ...budgetInput,
              monthly_budget: e.target.value,
            })
          }
          placeholder="50000"
        />
      </div>

      <div className="input-group">
        <label>Petrol Liters</label>
        <input
          type="number"
          value={budgetInput.petrol_liters}
          onChange={(e) =>
            setBudgetInput({
              ...budgetInput,
              petrol_liters: e.target.value,
            })
          }
          placeholder="100"
        />
      </div>

      <div className="input-group">
        <label>Diesel Liters</label>
        <input
          type="number"
          value={budgetInput.diesel_liters}
          onChange={(e) =>
            setBudgetInput({
              ...budgetInput,
              diesel_liters: e.target.value,
            })
          }
          placeholder="50"
        />
      </div>

      <div className="input-group">
        <label>LPG Cylinders</label>
        <input
          type="number"
          value={budgetInput.lpg_cylinders}
          onChange={(e) =>
            setBudgetInput({
              ...budgetInput,
              lpg_cylinders: e.target.value,
            })
          }
          placeholder="2"
        />
      </div>

      <div className="input-group">
        <label>Groceries Cost</label>
        <input
          type="number"
          value={budgetInput.groceries_cost}
          onChange={(e) =>
            setBudgetInput({
              ...budgetInput,
              groceries_cost: e.target.value,
            })
          }
          placeholder="15000"
        />
      </div>

      <div className="input-group">
        <label>Electricity Cost</label>
        <input
          type="number"
          value={budgetInput.electricity_cost}
          onChange={(e) =>
            setBudgetInput({
              ...budgetInput,
              electricity_cost: e.target.value,
            })
          }
          placeholder="3000"
        />
      </div>

      <div className="input-group">
        <label>Medical Cost</label>
        <input
          type="number"
          value={budgetInput.medical_cost}
          onChange={(e) =>
            setBudgetInput({
              ...budgetInput,
              medical_cost: e.target.value,
            })
          }
          placeholder="2000"
        />
      </div>
    </div>

    <button className="predict-btn" onClick={predictBudget}>
      Predict Budget
    </button>

    {budgetResult && (
      <div className="prediction-results">
        <h3 className="result-section-title">Extra Monthly Cost</h3>

        <div className="result-card">
          <h4>Petrol Extra Cost</h4>
          <p>₹{budgetResult.petrol_extra_cost}</p>
        </div>

        <div className="result-card">
          <h4>Diesel Extra Cost</h4>
          <p>₹{budgetResult.diesel_extra_cost}</p>
        </div>

        <div className="result-card">
          <h4>LPG Extra Cost</h4>
          <p>₹{budgetResult.lpg_extra_cost}</p>
        </div>

        <div className="result-card">
          <h4>Groceries Extra Cost</h4>
          <p>₹{budgetResult.groceries_extra_cost}</p>
        </div>

        <div className="result-card">
          <h4>Electricity Extra Cost</h4>
          <p>₹{budgetResult.electricity_extra_cost}</p>
        </div>

        <div className="result-card">
          <h4>Medical Extra Cost</h4>
          <p>₹{budgetResult.medical_extra_cost}</p>
        </div>

        <h3 className="result-section-title">Budget Summary</h3>

        <div className="result-card summary-card">
          <h4>Current Monthly Budget</h4>
          <p>₹{budgetResult.budget_summary.current_monthly_budget}</p>
        </div>

        <div className="result-card summary-card">
          <h4>Recommended Next Month Budget</h4>
          <p>₹{budgetResult.budget_summary.recommended_next_month_budget}</p>
        </div>

        <div className="result-card summary-card">
          <h4>Additional Budget Required</h4>
          <p>₹{budgetResult.budget_summary.additional_budget_required}</p>
        </div>
      </div>
    )}
  </div>
)}

{activePanel === "liveRiskNews" && (
  <div className="slide-panel">
    <div className="panel-header">
      <h2>Live Risk News</h2>

      <div>
        <button className="refresh-btn" onClick={fetchLiveRiskNews}>
          Refresh
        </button>

        <button onClick={() => setActivePanel(null)}>✕</button>
      </div>
    </div>

    {liveRiskNews ? (
      <div className="risk-news-box">
        <div className="score-row">
          <div className="score-card">
            <h4>War Score</h4>
            <p>{liveRiskNews.war_score}</p>
          </div>

          <div className="score-card">
            <h4>Shipping Score</h4>
            <p>{liveRiskNews.shipping_score}</p>
          </div>

          <div className="score-card">
            <h4>News Sentiment</h4>
            <p>{liveRiskNews.news_sentiment}</p>
          </div>
        </div>

        <NewsSection title="War News" items={liveRiskNews.war_news} />

        <NewsSection
          title="Shipping News"
          items={liveRiskNews.shipping_news}
        />

        <NewsSection
          title="Economic News"
          items={liveRiskNews.economic_news}
        />
      </div>
    ) : (
      <p>Loading live risk news...</p>
    )}
  </div>
)}
    </div>
  );
}
function NewsSection({ title, items }) {
  return (
    <div className="news-section">
      <h3>{title}</h3>

      {items && items.length > 0 ? (
        items.map((item, index) => (
          <div className="news-card" key={index}>
            <h4>{item}</h4>
          </div>
        ))
      ) : (
        <p className="empty-news">No news available.</p>
      )}
    </div>
  );
}
export default App;
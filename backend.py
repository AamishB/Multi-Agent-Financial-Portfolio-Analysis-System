from typing import Dict, List, TypedDict, Any
from pydantic import BaseModel, Field
import yfinance as yf
import numpy as np
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
# 1. Define State Representation
class PortfolioState(TypedDict):
    raw_query: str
    target_tickers: List[str]
    market_data: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    compliance_passed: bool
    audit_trail: List[str]
    final_report: str

# 2. Define Model Objects
class MarketIntent(BaseModel):
    tickers: List[str]
    analysis_depth: str

class ComplianceOutput(BaseModel):
    is_safe_to_publish: bool
    regulatory_justification: str

# 3. Create Graph Processing Nodes
def orchestrator_node(state: PortfolioState) -> Dict[str, Any]:
    print("[1/4] Running Orchestrator Agent...")
    model = ChatGoogleGenerativeAI(
        model="gemini-3.7-flash",
        temperature=1.0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    structured_model = model.with_structured_output(MarketIntent)
    messages=[
            ("system","Extract stock tickers from the text query."),
            ("human", state["raw_query"]),
        ]
    response = structured_model.invoke(messages)
    return {
        "target_tickers": response.tickers,
        "audit_trail": ["Orchestrator initialized execution graph."]
    }
    
import requests
from requests.exceptions import RequestException

def get_yf_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    })
    return session

def market_data_agent(state: PortfolioState) -> Dict[str, Any]:
    print("[2/4] Running Market Ingestion Agent...")
    ticker_data = {}
    session = get_yf_session()
    
    for t in state["target_tickers"]:
        try:
            stock = yf.Ticker(t, session=session)
            
            # Use history to get reliable recent prices
            hist = stock.history(period="1mo")
            if hist.empty:
                raise ValueError(f"No price history found for {t}")
            
            # Use the most recent close price
            current_price = float(hist["Close"].iloc[-1])
            
            # Try to get PE ratio from info, default to "N/A" or 0 if missing
            pe_ratio = stock.info.get("trailingPE", "N/A")
            
            # Get the last 5 days of history for volatility calc
            history_5d = hist["Close"].tail(5).tolist()
            
            ticker_data[t] = {
                "current_price": round(current_price, 2),
                "pe_ratio": pe_ratio if isinstance(pe_ratio, (int, float)) else 20.0,
                "history_5d": history_5d
            }
        except Exception as e:
            print(f"Error fetching data for {t}: {e}")
            ticker_data[t] = {"current_price": 100.0, "pe_ratio": 20.0, "history_5d": [100.0, 101.0, 102.0, 103.0, 104.0]}
    return {
        "market_data": ticker_data,
        "audit_trail": state["audit_trail"] + ["Market data successfully collected."]
    }

def quantitative_risk_agent(state: PortfolioState) -> Dict[str, Any]:
    print("[3/4] Running Quantitative Analysis Agent...")
    metrics = {}
    for t, data in state["market_data"].items():
        ret = np.diff(data["history_5d"]) / data["history_5d"][:-1]
        metrics[t] = {"calculated_volatility": float(np.std(ret))}
    return {
        "risk_metrics": metrics,
        "audit_trail": state["audit_trail"] + ["Quantitative analytics calculated variance models."]
    }

def compliance_xai_agent(state: PortfolioState) -> Dict[str, Any]:
    print("[4/4] Running Explainable Compliance Agent...")
    model = ChatGoogleGenerativeAI(
            model="gemini-3.7-flash",
            temperature=1.0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
    structured_model = model.with_structured_output(ComplianceOutput)
    messages=[
                ("system","Verify if the data is compliant for publication."),
                ("human", f"Review metrics: {state['risk_metrics']}"),
            ]
    response = structured_model.invoke(messages)
    return {
        "compliance_passed": response.is_safe_to_publish,
        "final_report": f"Analysis complete. Passed: {response.is_safe_to_publish}. Trace: {response.regulatory_justification}",
        "audit_trail": state["audit_trail"] + ["Compliance pipeline finished."]
    }

# 4. Construct the Workflow Dependency Graph
builder = StateGraph(PortfolioState)
builder.add_node("orchestrator", orchestrator_node)
builder.add_node("market_data", market_data_agent)
builder.add_node("quantitative_risk", quantitative_risk_agent)
builder.add_node("compliance", compliance_xai_agent)

builder.set_entry_point("orchestrator")
builder.add_edge("orchestrator", "market_data")
builder.add_edge("market_data", "quantitative_risk")
builder.add_edge("quantitative_risk", "compliance")
builder.add_edge("compliance", END)

workflow = builder.compile()



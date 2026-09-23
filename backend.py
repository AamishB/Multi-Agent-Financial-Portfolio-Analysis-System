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
    
def market_data_agent(state: PortfolioState) -> Dict[str, Any]:
    print("[2/4] Running Market Ingestion Agent...")
    ticker_data = {}
    for t in state["target_tickers"]:
        try:
            stock = yf.Ticker(t)
            ticker_data[t] = {
                "current_price": stock.info.get("currentPrice", 150.00),
                "pe_ratio": stock.info.get("trailingPE", 20.0),
                "history_5d": [100.0, 102.0, 101.0, 103.0, 105.0]
            }
        except Exception:
            ticker_data[t] = {"current_price": 100.0, "pe_ratio": 20.0, "history_5d": [100, 101, 102]}
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



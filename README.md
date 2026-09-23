# Multi-Agent Financial Portfolio Analysis

[🌐 Visit the Live Website](https://multi-agent-financial-portfolio-analysis-system.streamlit.app/)

A small LangGraph application that analyzes a portfolio request through four agents:

1. **Orchestrator** extracts stock tickers from the request.
2. **Market data** collects prices and valuation data from Yahoo Finance.
3. **Risk analysis** calculates basic volatility metrics.
4. **Compliance** reviews the results and produces a final report.

## Run the Streamlit app

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Google API key

Copy the example environment file:

```bash
copy .env.example .env
```

Then add your key to `.env`:

```env
GOOGLE_API_KEY=your-google-api-key
```

Keep `.env` private. It is ignored by Git.

### 3. Start the frontend

```bash
streamlit run frontend.py
```

Enter a request such as:

```text
Check recent volatility and compliance risks for AAPL and GOOG.
```

## Project structure

```text
backend.py       Agent functions and LangGraph workflow
frontend.py      Streamlit user interface
requirements.txt Python dependencies
.env.example     Environment variable template
```

## Run the workflow without Streamlit

Import the compiled workflow from `backend.py` and provide the expected portfolio state, or add a small runner script for your integration.

## Notes

- Market data comes from Yahoo Finance and may be delayed or incomplete.
- The compliance result is an application output, not legal or financial advice.
- For deployment, configure `GOOGLE_API_KEY` in the platform's secret manager instead of committing `.env`.

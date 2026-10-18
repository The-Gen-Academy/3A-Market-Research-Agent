# Market Research AI Agent — Keenable Edition

An AI-powered market research tool built with Streamlit, LangGraph, LangChain,
Google Gemini, and Keenable Search. It discovers three competitors, researches each one,
and produces structured competitor reports.

## Project layout

```text
Market Research Agent/
├── app.py
├── keenable_client.py
├── keenable_tools.py
├── Architecture.png
├── requirements.txt
├── tests/
└── .env.example
```

## Setup

Requires Python 3.10+ and a Gemini API key.
Keenable works without a key, but a Keenable API key raises the public rate limit.

Create `.env` from `.env.example`:

```text
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
KEENABLE_API_KEY=keen_your_keenable_api_key_here
```

Never commit your real API key.

Then run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Enter a company or product name and click **Run Research Pipeline**.

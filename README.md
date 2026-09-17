# Multi-Agent Research Assistant

This project contains a Multi-Agent Technical Research Assistant orchestrated by LangGraph.

## Run the application

Install the packages from `requirements.txt`, then start the API:

```powershell
uvicorn fastapi_app:app --reload --port 8000
```

In a second terminal, start the Streamlit client:

```powershell
streamlit run streamlit_app.py
```

The chat endpoint uses Server-Sent Events. Each conversation keeps its LangGraph checkpoint using the Streamlit session ID, and the UI displays workflow stages while the final answer is streamed. Set `API_BASE` when the API is hosted somewhere other than `http://localhost:8000`.
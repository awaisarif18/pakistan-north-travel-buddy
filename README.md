# Pakistan North Tours RAG

A minimal PDF chatbot project using Gemini, ChromaDB, and Streamlit.

## Current milestone

Environment setup and local PDF extraction are ready. Embedding, chat, evaluation,
and deployment will follow after review of the extracted chunks.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ingest.py
```

The script reads `pakistan-north-tours-final.pdf` from the project root and writes
`data/pages.json` and `data/chunks.json`. It preserves physical PDF page numbers,
keeps detected fare tables together, and creates stable chunk IDs. Chunk sizes
target approximately 400–700 tokens using a local character estimate. Headings
stay with their following paragraph where practical; chunks within a section overlap.
The script makes no API calls.

Keep your key in `.env`, using `.env.example` as a reference. The existing `.env`
is preserved. Secrets, the PDF, and extracted content are ignored by Git.

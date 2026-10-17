# Pakistan North Tours RAG

A minimal PDF chatbot project using Gemini, ChromaDB, and Streamlit.

## Current milestone

PDF extraction, persistent Gemini embeddings, and semantic retrieval are ready.
Chat, evaluation, and deployment are not implemented yet.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ingest.py
.\.venv\Scripts\python.exe ingest.py --embed
.\.venv\Scripts\python.exe rag.py
```

The script reads `pakistan-north-tours-final.pdf` from the project root and writes
`data/pages.json` and `data/chunks.json`. It preserves physical PDF page numbers,
keeps detected fare tables together, and creates stable chunk IDs. Chunk sizes
target approximately 400–700 tokens using a local character estimate. Headings
stay with their following paragraph where practical; chunks within a section overlap.
Extraction makes no API calls. `--embed` reads the saved chunks without extracting
the PDF again, saves vectors to `data/chroma`, and skips IDs already indexed.
Rate limits and temporary server errors get up to four attempts with backoff.

Documents and queries share the configured embedding model and 3072 dimensions,
with the model's document/query retrieval formatting. Chroma uses cosine distance.
`rag.py` runs five baseline queries, retrieves five chunks per question, displays
the top three IDs and page ranges, and saves full passages to
`data/retrieval_results.json`. Query embeddings are cached locally to avoid repeat
API calls. To try one question, run `python rag.py "Your question"`.

Keep your key in `.env`, using `.env.example` as a reference. The existing `.env`
is preserved. Secrets, the PDF, and extracted content are ignored by Git.

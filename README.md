# 🧠 AI Compliance Assistant (RAG + Streamlit)
# Hamza Siddiqui
# www.linkedin.com/in/hamsid

# Summary
A lightweight, local-first **RAG (Retrieval-Augmented Generation)** app that evaluates uploaded **policy/evidence documents** (PDF/DOCX/TXT) against a **control checklist** (e.g., ISO 27001, SOC 2).  
It retrieves the most relevant information, assesses **Coverage**, identifies **Gaps**, evaluates **Risks**, and generates **Recommendations** — exporting the results as a clean CSV file.

---

## ✨ Features
- **Streamlit interface** — upload files, view search results, and download CSVs.
- **RAG workflow** — combines document retrieval with LLM-based auditing.
- **ChromaDB local storage** — fast, private, meaning-based search (semantic retrieval).
- **LLM Scoring** — coverage (Covered/Partially/Not Covered), gap summaries, risks, and recommendations.
- **Exportable Results** — one-click CSV download of all audit findings.

---

## 🧩 Architecture Overview
1. **Upload** documents → Extract & clean text.
2. **Chunk** text into token-based segments.
3. **Embed** chunks (convert meaning to numeric vectors).
4. **Store** chunks + embeddings in a local Chroma vector database.
5. **Retrieve** evidence for each control from `controls.csv`.
6. **Evaluate** each control using an LLM (gpt-4o-mini).
7. **Display & Export** structured JSON → interactive table → downloadable CSV.

---

## 🗂️ Project Structure
```
.
├─ interface.py        # Streamlit UI (upload, test search, run audit, export CSV)
├─ loaders.py          # Text extraction, cleaning, and chunking
├─ rag_client.py       # OpenAI API client + embeddings creation
├─ vectorstore.py      # Local ChromaDB vector storage and semantic search
├─ evaluator.py        # LLM-based audit evaluation and JSON output
├─ controls.csv        # Control checklist (id, control, question)
├─ test_LLM.py         # API sanity test for verifying GPT connectivity
├─ .env                # API key storage (DO NOT COMMIT)
└─ chroma/             # Local Chroma database folder (auto-created)
```

---

## ⚙️ Prerequisites
- **Python 3.10+**
- **OpenAI API Key** with:
  - `gpt-4o-mini` (model)
  - `text-embedding-3-small` (embedding model)

---

## 🚀 Setup & Installation

### 1️⃣ Create a Virtual Environment
**Windows**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 2️⃣ Install Dependencies
```bash
pip install streamlit openai chromadb pypdf docx2txt python-dotenv pandas tiktoken pydantic
```

(Optional)
```bash
pip freeze > requirements.txt
```

---

### 3️⃣ Add Your OpenAI API Key
Create a file named `.env` in the root folder:
```env
OPENAI_API_KEY=sk-yourapikeyhere
```

> ⚠️ **Never upload your `.env` file to GitHub, `.env` file stores the API Key**.  
> Commit only a template instead:
> ```bash
> echo "OPENAI_API_KEY=" > .env.example
> ```

---

### 4️⃣ Run the App
```bash
streamlit run interface.py
```

Streamlit will open your browser with the app at:
```
http://localhost:8501
```

---

## 🧠 How to Use

1. **Upload** your policy or audit documents (PDF/DOCX/TXT).
2. *(Optional)* Test the **Quick Retrieval** to verify semantic search.
3. **Run Scoring** to evaluate all control questions from `controls.csv`.
4. **Download** your compliance audit as a CSV report.

---

### ✅ Example controls.csv
```csv
id,control,question
AC-01,Access Control,"Do you enforce least privilege for all roles and review access regularly?"
LM-01,Logging & Monitoring,"What mechanisms log user and system activity, and how often are they reviewed?"
CM-01,Change Management,"Is there a documented change management and approval process?"
IR-01,Incident Response,"Do you test your incident response process regularly and maintain escalation steps?"
```

---

## 🧩 Output Interpretation

| Column | Meaning |
|---------|----------|
| **Control ID** | Reference from `controls.csv`. |
| **Control (Topic discussed)** | The control category or topic. |
| **Coverage** | Whether the document covers the control (*Covered / Partially / Not Covered*). |
| **Gaps** | What’s missing in uploaded docs relative to the checklist. |
| **Risk** | What could go wrong if the gap isn’t addressed. |
| **Recommendation** | Suggested corrective action. |
| **Confidence** | How confident the model is in its judgement (0–1). |

---
## 🧾 Troubleshooting
### 🟡 CSV shows weird symbols (â€¢, â€™)
That’s an **encoding issue** on Windows Excel.  
Fix it by exporting with:
```python
df.to_csv(index=False).encode("utf-8-sig")
```
or import in Excel using **UTF-8 encoding** (`Data → From Text/CSV → File Origin: 65001 Unicode`).
---
### 🔴 Resetting the Vector Store
If you need a clean start:
- Use the **“Reset vector store”** button in the sidebar.
- It deletes the local Chroma collection and reinitializes it.

---

## 🧪 Quick LLM Test
You can verify your OpenAI API key is working:
```bash
python test_LLM.py
```

Expected output:
```
hello
```

---

## 🧠 Summary
This system is a **proof-of-concept AI Compliance Assistant** that uses:
- **RAG** for semantic retrieval  
- **LLM** for contextual reasoning  
- **Streamlit** for interactive auditing  
- **Chroma** for local vector storage  

Together, it automates compliance gap detection from your uploaded documents.

---

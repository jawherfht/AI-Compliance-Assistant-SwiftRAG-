# 🛡️ SwiftGuard AI – SWIFT CSCF Compliance Assistant

### Jawher Farhat
AI Engineering Student – ESPRIT

## 📖 Overview

SwiftGuard AI is an AI-powered compliance assistant designed to simplify the analysis of the SWIFT Customer Security Controls Framework (CSCF). The platform leverages Retrieval-Augmented Generation (RAG), Natural Language Processing (NLP), and local Large Language Models (LLMs) to automatically extract SWIFT security controls, generate concise summaries, identify keywords, and enable intelligent semantic search.

The system helps cybersecurity teams, auditors, and compliance officers quickly navigate SWIFT CSCF requirements without manually reviewing hundreds of pages of documentation.

---

## ✨ Features

- Automatic extraction of SWIFT CSCF security controls
- Detection of control IDs and corresponding pages
- AI-generated control summaries
- Keyword extraction for rapid navigation
- Semantic search using ChromaDB
- RAG-powered compliance chatbot
- Local deployment with Ollama (Gemma 3 + Nomic Embeddings)
- Streamlit-based interactive interface
- Compliance knowledge base generation

---

## 🧩 Architecture Overview

1. Upload SWIFT CSCF PDF document
2. Extract and identify controls (1.1, 1.2, 2.4, etc.)
3. Generate control summaries using local LLMs
4. Extract keywords for each control
5. Store summaries and embeddings in ChromaDB
6. Perform semantic retrieval through RAG
7. Query controls using an intelligent chatbot
8. Export structured compliance knowledge

---

## 🗂️ Project Structure

```text
.
├── interface.py             # Streamlit UI
├── loaders.py               # Document loading and processing
├── vectorstore.py           # ChromaDB integration
├── rag_client.py            # RAG pipeline
├── swift_parser.py          # SWIFT CSCF control extraction
├── control_summarizer.py    # Control summarization
├── keyword_extractor.py     # Keyword extraction
├── database.py              # Knowledge base management
├── controls.csv             # Extracted controls
├── swift_controls.csv       # SWIFT controls dataset
├── control_summaries.json   # Generated summaries
├── requirements.txt
└── chroma/                  # Local vector database
```

---

## ⚙️ Technologies Used

- Python
- Streamlit
- ChromaDB
- Ollama
- Gemma 3 (4B)
- Nomic Embed Text
- LangChain
- RAG
- NLP
- PDF Processing

---

## 🚀 Installation

### Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Ollama Models

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

### Run the Application

```bash
streamlit run interface.py
```

---

## 🧠 Usage

### SWIFT CSCF Pipeline

1. Upload the SWIFT CSCF PDF.
2. Extract all security controls.
3. Generate summaries and keywords.
4. Build the compliance knowledge base.
5. Query controls through the chatbot interface.

### Generic RAG Mode

1. Upload compliance documents.
2. Index content in ChromaDB.
3. Ask questions using semantic search.

---

## 🎯 Use Cases

- SWIFT CSCF compliance analysis
- Cybersecurity audits
- Security control review
- Compliance knowledge management
- Regulatory requirement exploration
- Security awareness and training

---

## 👨‍💻 Author

Jawher Farhat

AI Engineering Student – ESPRIT

Internship Project – STB Bank

---

## 🛡️ SwiftGuard AI

Making SWIFT CSCF compliance analysis faster, smarter, and fully local with AI.
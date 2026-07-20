import os
import streamlit as st
import pandas as pd
import tempfile
import json

# Load text extractors, cleaner, and chunker
from loaders import extract_text_pdf, extract_text_docx, clean_text, chunk_by_tokens

# Vector store helpers to save and search chunks
from vectorstore import index_document, search, reset_collection

# Evaluator that scores one control using retrieved evidence
from evaluator import evaluate_control

# SWIFT integration modules
from swift_parser import extract_controls, generate_control_pdfs
from control_summarizer import summarize_controls
from keyword_extractor import extract_keywords
from database import initialize_database, seed_database, update_database_with_extras

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTROLS_CSV_PATH = os.path.join(BASE_DIR, "controls.csv")


# 1. Streamlit page setup
st.set_page_config(page_title="Compliance Assistant", layout="wide")
st.title("Compliance Assistant W/ RAG")

# Model Validation check
try:
    import ollama
    ollama.list()
except Exception as e:
    st.warning(f"⚠️ Ollama might not be running. Start Ollama locally. Error: {e}")

# 2. Sidebar controls
with st.sidebar:
    st.subheader("Utilities")
    if st.button("Reset vector store"):
        reset_collection()
        st.success("Cleared the local vector DB")

# Tabs
tab1, tab2 = st.tabs(["Generic RAG Audit", "SWIFT CSCF Pipeline"])

with tab1:
    # 3. File upload
    uploaded = st.file_uploader(
        "Upload PDF DOCX or TXT",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if uploaded:
        with st.spinner("Ingesting documents..."):
            for up in uploaded:
                try:
                    filename_lower = up.name.lower()
                    # Security: Mime type validation
                    if not (up.type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"] or filename_lower.endswith(('.pdf', '.docx', '.txt'))):
                        st.error(f"Unsupported file type: {up.name}")
                        continue

                    if up.type == "application/pdf" or filename_lower.endswith(".pdf"):
                        text = extract_text_pdf(up.read())
                    elif filename_lower.endswith(".docx"):
                        text = extract_text_docx(up.read())
                    else:
                        text = up.read().decode("utf-8", errors="ignore")

                    text = clean_text(text)

                    # Smaller chunks so Ollama's embedding context isn't exceeded
                    chunks = chunk_by_tokens(text, chunk_size=300, overlap=50)

                    index_document(doc_id=up.name, chunks=chunks, metadata={"filename": up.name})
                except Exception as e:
                    st.error(f"Failed to ingest {up.name}: {e}")

        st.success(f"Ingested {len(uploaded)} document(s) into the vector store")


    # 4. Quick retrieval sanity check
    st.subheader("Quick retrieval test")
    q = st.text_input(
        "Type a control style question to make sure that Vector search works properly (Optional)",
        value="Do you enforce least privilege for all roles"
    )

    if st.button("Search"):
        try:
            res = search(q, k=5)
            hits = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            dists = res.get("distances", [[]])[0]

            if not hits:
                st.info("No matches found. Have you uploaded and ingested a document yet?")
            else:
                st.write("Top matches")
                for i, chunk in enumerate(hits):
                    meta = metas[i] if i < len(metas) else {}
                    dist = dists[i] if i < len(dists) else None
                    if meta.get('type') == 'SWIFT':
                        with st.expander(f"{meta.get('control_id', 'N/A')} - {meta.get('title', 'N/A')}"):
                            st.write(f"**Control ID:** {meta.get('control_id', 'N/A')}")
                            st.write(f"**Title:** {meta.get('title', 'N/A')}")
                            st.write(f"**Distance:** {dist}")
                            st.write("**Summary:**")
                            st.write(chunk)
                    else:
                        with st.expander(f"Match {i + 1}  file={meta.get('filename', 'unknown')}  distance={dist}"):
                            st.write(chunk)
        except Exception as e:
            st.error(f"Search failed: {e}")


    # 5. Tiny checklist to demonstrate scoring flow
    st.subheader("Score a tiny checklist")

    if not os.path.exists(CONTROLS_CSV_PATH):
        st.warning(
            f"controls.csv not found at {CONTROLS_CSV_PATH}. "
            "Please ensure the generic checklist exists."
        )
    else:
        controls = pd.read_csv(CONTROLS_CSV_PATH)

        if st.button("Run scoring"):
            rows = []
            errors = []

            with st.spinner("Scoring controls..."):
                for _, r in controls.iterrows():
                    try:
                        data = evaluate_control(
                            control_id=r["id"],
                            control_name=r["control"],
                            question=r["question"],
                            k=5
                        )
                        rows.append({
                            "Control ID": r["id"],
                            "Control (Topic discussed)": r["control"],
                            "Coverage (How strong the evidence in documents provided is)": data.get("coverage"),
                            "Gaps (What's missing in the uploaded docs relative to the checklist)": "\n".join(f"• {g}" for g in data.get("gap_summary", [])),
                            "Risk (What could go wrong if it isn't fixed)": data.get("risk"),
                            "Recommendation (What to do about that gap/problem)": "\n".join(f"• {rec}" for rec in data.get("recommendation", [])),
                            "Confidence (How confident AI is about its judgement)": data.get("confidence"),
                        })
                    except Exception as e:
                        errors.append(f"{r['id']}: {e}")

            if errors:
                st.warning(f"{len(errors)} control(s) failed to score:\n" + "\n".join(errors))

            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df.style.set_properties(**{'white-space': 'pre-wrap'}), use_container_width=True)

                st.download_button(
                    "Download CSV",
                    df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="compliance_results.csv",
                    mime="text/csv"
                )

with tab2:
    st.header("SWIFT CSCF Integration Pipeline")
    st.markdown("Upload a SWIFT CSCF PDF to extract controls, summarize them, generate keywords, and store them into SQLite and Vector DB.")
    
    swift_pdf = st.file_uploader("Upload SWIFT CSCF PDF", type=["pdf"], key="swift")
    
    if swift_pdf:
        if st.button("Run SWIFT Pipeline"):
            with st.spinner("Processing SWIFT Pipeline..."):
                try:
                    # 1. Save PDF temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(swift_pdf.read())
                        tmp_path = tmp.name
                    
                    st.info("1/5: Extracting controls from PDF...")
                    controls = extract_controls(tmp_path)
                    if controls:
                        generate_control_pdfs(
                            tmp_path,
                            controls,
                            os.path.join(BASE_DIR, "generated_controls"),
                        )
                    os.remove(tmp_path)
                    
                    if not controls:
                        st.error("No controls found in PDF.")
                    else:
                        # Save to CSV
                        csv_path = "swift_controls.csv"
                        pd.DataFrame(controls).to_csv(csv_path, index=False)
                        st.success(f"Extracted {len(controls)} controls.")
                        
                        st.info("2/5: Summarizing controls using gemma3:4b (This may take a while)...")
                        summaries = summarize_controls(csv_path, "control_summaries.json")
                        
                        st.info("3/5: Extracting keywords using KeyBERT...")
                        keywords = extract_keywords("control_summaries.json", "keywords.json")
                        
                        st.info("4/5: Saving to SQLite Database...")
                        initialize_database()
                        seed_database(csv_path)
                        update_database_with_extras("control_summaries.json", "keywords.json")
                        st.success("Controls, summaries, and keywords stored in swift.db")
                        
                        st.info("5/5: Indexing SWIFT summaries into Vector DB...")
                        reset_collection() # Clear old documents to prevent mixing SWIFT with generic RAG
                        swift_df = pd.read_csv(csv_path)
                        titles_dict = dict(zip(swift_df['control_id'].astype(str), swift_df['title']))
                        
                        for c_id, text in summaries.items():
                            chunks = chunk_by_tokens(text, chunk_size=300, overlap=50)
                            title = titles_dict.get(str(c_id), "Unknown Title")
                            index_document(doc_id=f"SWIFT_{c_id}", chunks=chunks, metadata={"control_id": c_id, "title": title, "type": "SWIFT"})
                        st.success("SWIFT summaries successfully ingested into ChromaDB for RAG chatbot.")
                        
                        st.balloons()
                except Exception as e:
                    st.error(f"Pipeline error: {e}")

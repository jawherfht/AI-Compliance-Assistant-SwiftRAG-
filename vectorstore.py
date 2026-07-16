import chromadb, hashlib
from chromadb.config import Settings
from rag_client import embed_texts

# Stores the chunks of data split from loaders.py and then undertood by rag_client (vectors) into local chroma database.
# Local chroma database stores not only the vectors but also orignal text + metadata inside local chroma db.
# So when looking for text/data it looks for relevant text/data by meaning not by keywords.
# On search: embed the question (via rag_client) and return the nearest chunks by meaning (nearest neighbors).
# Understanding = embeddings.
# Finding = vector search.

# Persistent DB in ./chroma folder
chroma = chromadb.PersistentClient(path="./chroma", settings=Settings(anonymized_telemetry=False))
collection = chroma.get_or_create_collection("docs", embedding_function=None)

# Helps create ID numbers for chunks so we can avoid duplicates issues
def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

# Saves the chunks of plain text from loader.py and stores the chunks of data into local chroma database so we can search for them later    
def index_document(doc_id: str, chunks: list[str], metadata: dict | None = None):
    # dedupe by hash in case the same file is re ingested
    ids, docs, metas = [], [], []
    for i, ch in enumerate(chunks):
        hid = f"{doc_id}_{_hash(ch)}_{i}"
        ids.append(hid); docs.append(ch)
        metas.append({"doc_id": doc_id, "order": i, **(metadata or {})})
    vectors = embed_texts(docs)
    collection.add(ids=ids, embeddings=vectors, documents=docs, metadatas=metas)

def reset_collection():
    chroma.delete_collection("docs")
    global collection
    collection = chroma.get_or_create_collection("docs", embedding_function=None)


# Finds the top matching chunks for a question. It embeds the question, searches nearest vectors, and returns the best matches.
# Embedding a question = turn the question into numbers so you can find the nearest chunks by meaning.
def search(query: str, k=5):
    if not query or not query.strip():
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    qv = embed_texts([query])[0]
    return collection.query(
        query_embeddings=[qv],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

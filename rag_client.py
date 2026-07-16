import ollama

CHAT_MODEL = "gemma3:4b"
EMBED_MODEL = "nomic-embed-text"

def embed_texts(texts: list[str]) -> list[list[float]]:
    res = []
    for txt in texts:
        resp = ollama.embeddings(model=EMBED_MODEL, prompt=txt)
        res.append(resp["embedding"])
    return res

def search_control_by_id(control_id):
    import sqlite3
    conn = sqlite3.connect("swift.db")
    result = conn.execute(
        "SELECT * FROM controls WHERE control_id = ?",
        (control_id,)
    ).fetchone()
    conn.close()
    return result
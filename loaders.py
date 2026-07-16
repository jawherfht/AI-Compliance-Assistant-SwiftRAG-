from pypdf import PdfReader
import docx2txt, io, tempfile, re, unicodedata
import tiktoken
# loaders.py is repsonsible for scanning text from pdf or doc, cleaning text by fixing the weird gaps, spaces and extra texts, and splits the texts into chunks for vector storage.

# Reads pdf file and pulls out the plain texts
def extract_text_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# Reads Word files and pulls out the plain texts
def extract_text_docx(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
        tmp.write(file_bytes); tmp.flush()
        return docx2txt.process(tmp.name)
    
# Organizes the text so it's easier to search by removing extra spaces, dashes, etc.
def clean_text(txt: str) -> str:
    # normalize unicode to avoid funky characters
    txt = unicodedata.normalize("NFKC", txt)

    # fix words split by a line break with a dash, like securi-\n
    txt = re.sub(r"(\w)[-–]\n(\w)", r"\1\2", txt)

    # join single newlines inside paragraphs into spaces
    txt = re.sub(r"(?<!\n)\n(?!\n)", " ", txt)

    # collapse big whitespace
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)

    # drop stand alone page numbers
    txt = re.sub(r"\n\s*\d+\s*\n", "\n", txt)
    return txt.strip()

# Puts cleaned text into chunks as part of vector search process
def chunk_by_tokens(text: str, chunk_size=800, overlap=120, enc_name="o200k_base"):
    enc = tiktoken.get_encoding(enc_name)
    toks = enc.encode(text)
    chunks = []
    start = 0
    while start < len(toks):
        end = min(len(toks), start + chunk_size)
        chunk = enc.decode(toks[start:end])
        chunks.append(chunk)
        if end == len(toks): break
        start = max(0, end - overlap)
    return chunks

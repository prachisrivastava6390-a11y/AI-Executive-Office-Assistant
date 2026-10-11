from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from docx import Document


KNOWLEDGE_BASE_PATH = Path("data/knowledge_base.txt")

model = SentenceTransformer("all-MiniLM-L6-v2")


def load_knowledge_base():
    return KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")


def extract_pdf_text(file):
    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text


def extract_docx_text(file):
    document = Document(file)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_txt_text(file):
    return file.read().decode("utf-8")


def extract_document_text(file):

    file_type = file.name.lower()

    if file_type.endswith(".pdf"):
        return extract_pdf_text(file)

    elif file_type.endswith(".docx"):
        return extract_docx_text(file)

    elif file_type.endswith(".txt"):
        return extract_txt_text(file)

    else:
        return ""


def search_knowledge_base(user_request):

    knowledge = load_knowledge_base()

    chunks = knowledge.split("\n\n")

    embeddings = model.encode(chunks)

    index = faiss.IndexFlatL2(embeddings.shape[1])

    index.add(embeddings)

    question_embedding = model.encode([user_request])

    distances, indices = index.search(question_embedding, 3)

    results = []

    for index_number in indices[0]:
        results.append(chunks[index_number])

    return "\n\n".join(results)

def search_document(document_text, user_request):

    chunks = document_text.split("\n\n")

    embeddings = model.encode(chunks)

    index = faiss.IndexFlatL2(embeddings.shape[1])

    index.add(embeddings)

    question_embedding = model.encode([user_request])

    distances, indices = index.search(question_embedding, 3)

    results = []

    for index_number in indices[0]:
        results.append(chunks[index_number])

    return "\n\n".join(results)
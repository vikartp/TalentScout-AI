import chromadb
from langchain_openai import OpenAIEmbeddings

from app.config import OPENAI_API_KEY, OPENAI_API_BASE, CHROMA_PERSIST_DIR, EMBEDDING_MODEL

embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE,
)

chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_or_create_collection(name: str = "resumes"):
    return chroma_client.get_or_create_collection(name=name)

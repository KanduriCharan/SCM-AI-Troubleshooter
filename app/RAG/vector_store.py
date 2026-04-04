from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

def get_embeddings_function() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model = settings.embedding_model,
        api_key=settings.openai_api_key,
    )

def get_vector_store()-> Chroma:
    return Chroma(
        collection_name = settings.chroma_collection_name,
        embedding_function= get_embeddings_function(),
        persist_directory=settings.chroma_persist_directory,
    )
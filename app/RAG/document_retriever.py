from app.models.schemas import RetrievedEvidence
from app.RAG.vector_store import get_vector_store


def retrieve_document_evidence(query: str, k: int = 8) -> list[RetrievedEvidence]:
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(query, k=k)

    evidence = []
    for i, doc in enumerate(docs):
        metadata = doc.metadata or {}
        source_file = metadata.get("source_file", "uploaded_document")
        page = metadata.get("page", "unknown")

        evidence.append(
            RetrievedEvidence(
                source_id=f"RAG-{source_file}-{i}",
                source_type="uploaded_manual",
                title=f"{source_file} (page {page})",
                snippet=doc.page_content,
            )
        )

    return evidence
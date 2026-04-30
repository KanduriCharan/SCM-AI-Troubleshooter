from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.RAG.vector_store import get_vector_store
from docling.document_converter import DocumentConverter
from langchain_core.documents import Document

def extract_pdf_with_docling(file_path: Path) -> list[Document]:
    converter = DocumentConverter()
    result = converter.convert(str(file_path))

    markdown_text = result.document.export_to_markdown()

    return [
        Document(
            page_content=markdown_text,
            metadata={
                "source_file": file_path.name,
                "source_type": "uploaded manual",
                "parser": "docling",
            },
        )
    ]

def ingest_pdf(pdf_path: str) -> dict:
    file_path = Path(pdf_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF NOT FOUND: {pdf_path}")
    
    documents = extract_pdf_with_docling(file_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 150,
    )

    split_docs = splitter.split_documents(documents)

    for idx, doc in enumerate(split_docs):
        doc.metadata["source_file"] = file_path.name
        doc.metadata["chunk_index"] = idx
        doc.metadata["source_type"] = "uploaded manual"
        doc.metadata["parser"] = "docling"
    
    vector_store = get_vector_store()
    ids= [
        f"{file_path.stem}-chunk-{i}"
        for i in range(len(split_docs))
    ]
    vector_store.add_documents(documents=split_docs, ids=ids)

    return {
        "file_name": file_path.name,
        "pages_loaded": len(documents),
        "chunks_created": len(split_docs),
        "status": "indexed",
    }


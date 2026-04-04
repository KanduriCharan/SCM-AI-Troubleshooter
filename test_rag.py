from app.RAG.document_retriever import retrieve_document_evidence

query = "label printing failure warehouse troubleshooting"
results = retrieve_document_evidence(query=query, k=4)

print(f"Retrieved {len(results)} chunks\n")

for item in results:
    print("=" * 80)
    print("TITLE:", item.title)
    print("SOURCE TYPE:", item.source_type)
    print("SOURCE ID:", item.source_id)
    print("SNIPPET:")
    print(item.snippet[:800])
    print()
from app.retrieval.data_loader import load_canonical_docs, load_incidents, load_policies, load_live_transactions
from app.retrieval.transaction_lookup import get_transaction_by_id
from app.retrieval.hybrid_retriever import retrieve_evidence

print("Canonical docs:", len(load_canonical_docs()))
print("Incidents:", len(load_incidents()))
print("Policies:", len(load_policies()))
print("Live transactions:", len(load_live_transactions()))

tx = get_transaction_by_id("RCV-1002")
print("Transaction:", tx)

evidence = retrieve_evidence(
    raw_error_message="Receiving transaction failed due to supplier site mapping missing.",
    transaction_snapshot=tx,
)

print("\nTop evidence:")
for item in evidence:
    print(item.source_id, "|", item.source_type, "|", item.title)
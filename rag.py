import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DATA_PATH = "chroma_db"

POLICIES = [
    {
        "id": "policy_returns",
        "text": (
            "Apex TechGear Return Policy: Customers may return any eligible product within 30 calendar days "
            "of carrier delivery. Items must be unopened or in gently-tested condition with all original packaging "
            "and accessories. Returns are free of restocking fees. Prepaid return shipping labels are generated automatically. "
            "Items delivered more than 30 calendar days ago are strictly outside the return window and ineligible for a return."
        )
    },
    {
        "id": "policy_cancellations",
        "text": (
            "Cancellation & Billing Hold Policy: Orders can be cancelled instantly before shipment. "
            "When an order is cancelled, we immediately release our claim on the funds. However, credit card companies "
            "and banks often display this as a 'Pending Charge' or temporary pre-authorization hold. "
            "This hold typically disappears from the customer's online statement within 24 to 72 business hours depending on their bank. "
            "No actual money was deducted by Apex TechGear."
        )
    },
    {
        "id": "policy_shipping",
        "text": (
            "Shipping & Delivery Policy: Standard delivery takes 3-5 business days. Express takes 1-2 business days. "
            "Live tracking numbers are activated within 24 hours of package handoff to FedEx, UPS, or USPS. "
            "If a package is marked 'In-Transit' past the estimated delivery window by more than 4 business days, "
            "we initiate a priority trace investigation with the carrier."
        )
    },
    {
        "id": "policy_damaged",
        "text": (
            "Damaged, Defective, or Lost Items Policy: If an item arrives broken, defective, or package is confirmed lost "
            "by the carrier, Apex TechGear provides an immediate, complimentary replacement with expedited overnight shipping, "
            "or a full 100% refund. The customer must report damaged items within 14 days of receipt."
        )
    },
    {
        "id": "policy_international",
        "text": (
            "International Orders & Customs: International shipments may incur customs duties and VAT as determined "
            "by the destination country's government. Apex TechGear covers standard shipping fees, but local import tariffs "
            "are the responsibility of the recipient."
        )
    }
]

def init_rag():
    chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    # Using standard default embedding model
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    
    collection = chroma_client.get_or_create_collection(
        name="company_policies",
        embedding_function=embedding_func
    )
    
    # Insert or update policies
    collection.upsert(
        ids=[p["id"] for p in POLICIES],
        documents=[p["text"] for p in POLICIES],
        metadatas=[{"source": "employee_handbook_v3"} for _ in POLICIES]
    )
    print("✅ Knowledge Base (RAG) updated with all comprehensive store policies!")

def search_knowledge_base(query: str, top_k: int = 2):
    chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    collection = chroma_client.get_or_create_collection(
        name="company_policies",
        embedding_function=embedding_func
    )
    
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    if results and "documents" in results and results["documents"]:
        return results["documents"][0]
    return []

if __name__ == "__main__":
    init_rag()
from zenml import step
from pymongo import MongoClient
from bson import ObjectId
import logging

# MongoDB client (sync)
client = MongoClient("mongodb://localhost:27017")
db = client["federated_db"]
collection = db["uploaded_files"]

def update_document(doc_id: str, status: str, accuracy: float) -> None:
    """Synchronous helper to update the document in MongoDB."""
    logging.info(f"Updating document in MongoDB... status={status}")

    try:
        obj_id = ObjectId(doc_id)
    except Exception as e:
        logging.error(f"Invalid document ID {doc_id}: {e}")
        return

    document = collection.find_one({"_id": obj_id})
    if not document:
        logging.error(f"No document found with ID: {doc_id}")
        return

    update_data = {
        "accuracy": accuracy,
        "status": status,
    }

    result = collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if result.modified_count > 0:
        logging.info(f"Updated document {doc_id} successfully")
    else:
        logging.warning(f"No changes made to document {doc_id}")

@step(enable_cache=False)
def status_update_step(doc_id: str, status: str, accuracy: float) -> None:
    """ZenML step to update MongoDB document status."""
    update_document(doc_id, status, accuracy)
    logging.info(
        f"Triggered update for document ID: {doc_id}, "
        f"status: {status}, accuracy: {accuracy}"
    )

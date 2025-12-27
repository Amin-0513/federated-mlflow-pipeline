from zenml import step
import motor.motor_asyncio
from bson import ObjectId
import asyncio
import logging
from datetime import datetime

# MongoDB client (async)
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client["federated_db"]
collection = db["uploaded_files"]

def doc_helper(doc):
    return {
        "id": str(doc["_id"]),
        "username": doc.get("username"),
        "filepath": doc.get("filepath"),
        "accuracy": doc.get("accuracy"),
        "uploaded_at": doc.get("uploaded_at"),
        "status": doc.get("status"),
    }

async def update_document(doc_id: str, status: str, accuracy: float):
    """Async helper to update the document in MongoDB."""

    try:
        obj_id = ObjectId(doc_id)
    except Exception as e:
        logging.error(f"Invalid document ID {id}: {e}")
        return

    document = await collection.find_one({"_id": obj_id})
    if not document:
        logging.error(f"No document found with ID: {id}")
        return

    update_data ={
        "id": str(document["_id"]),
        "username": document.get("username"),
        "filepath": document.get("filepath"),
        "accuracy": accuracy,
        "uploaded_at": document.get("uploaded_at"),
        "status": status,
    }
    result = await collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    if result.modified_count > 0:
        logging.info(f"Updated document {id} successfully")
    else:
        logging.warning(f"No changes made to document {id}")

@step
def status_update_step(doc_id: str, status: str, accuracy: float) -> None:
    """Synchronous wrapper for updating the MongoDB document."""
    asyncio.run(update_document(doc_id, status, accuracy))
    logging.info(f"Triggered update for document ID: {doc_id} with status: {status} and accuracy: {accuracy}")
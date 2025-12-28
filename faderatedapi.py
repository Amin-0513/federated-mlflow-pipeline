from fastapi import FastAPI, HTTPException
from bson import ObjectId
import motor.motor_asyncio
from pipeline.FL_Averaging import FL_Averaging

app = FastAPI(title="MongoDB Document API")

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client["federated_db"]          # Replace with your DB name
collection = db["uploaded_files"]    # Replace with your collection name

# Helper function to format MongoDB document
def doc_helper(doc):
    return {
        "id": str(doc["_id"]),
        "username": doc.get("username"),
        "filepath": doc.get("filepath"),
        "accuracy": doc.get("accuracy"),
        "uploaded_at": doc.get("uploaded_at"),
        "status": doc.get("status"),
    }

# Endpoint to get document by ID
@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    data_path = "./brain_tumor_dataset/"
    
    # Validate ObjectId
    try:
        obj_id = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    
    # Find document in DB
    document = await collection.find_one({"_id": obj_id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Call FL_Averaging
    # Assuming FL_Averaging accepts a list for path_model
    FL_Averaging(
    data_path=data_path,
    path_model=str(document.get("filepath")),
    doc_id=str(obj_id)  # convert to string
)

    
    return {
        "message": "Model combined successfully",
    }

import socket
import json
import os
from pymongo import MongoClient
import datetime
from datetime import datetime
HOST = '127.0.0.1'
PORT = 5001



# ================= MongoDB Setup =================
client = MongoClient("mongodb://localhost:27017/")
db = client["federated_db"]
files_collection = db["uploaded_files"]

os.makedirs("client_files", exist_ok=True)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

conn.sendall(b"Connection established")

while True:
    # Receive JSON header (1024 bytes)
    header = conn.recv(1024)
    if not header:
        break

    header = header.decode()

    if header.lower() == "close":
        print("Client requested to close connection")
        break

    metadata = json.loads(header)
    username = metadata["username"]
    filename = metadata["filename"]
    filesize = metadata["filesize"]

    print(f"User: {username}")
    print(f"Receiving file: {filename} ({filesize} bytes)")

    user_dir = os.path.join("client_files", username)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"
    filepath = f"client_files/{new_filename}"

    received = 0
    with open(filepath, "wb") as f:
        while received < filesize:
            data = conn.recv(4096)
            if not data:
                break
            f.write(data)
            received += len(data)
    files_collection.insert_one({
        "username": username, 
        "filepath": filepath,
        "accuracy": None,
        "status": "submitted",
        "uploaded_at": datetime.utcnow()
    })
    print(f"File saved at {filepath}")

conn.close()
server_socket.close()
print("Server closed")

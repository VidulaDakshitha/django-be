from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
from django.conf import settings


class MongoDBClient:
    def __init__(self):
        try:
            self.client = MongoClient(
                settings.MONGO_DB_HOST,
                serverSelectionTimeoutMS=5000  # 5 seconds timeout
            )
            self.client.server_info()  # Trigger exception if connection fails
            self.db = self.client["PearsChatDB"]
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")

    def get_chat_history(self, room_id, page=1, limit=10):
        collection = self.db["Chat"]
        skip = (page - 1) * limit
        query = {"room_id": room_id}
        projection = {"_id": 0, "room_id": 1, "sender": 1, "receiver": 1, "message": 1, "created_on": 1}
        cursor = collection.find(query, projection).sort("created_on", DESCENDING).skip(skip).limit(limit)
        results = list(cursor)  # Convert the cursor to a list
        return results[::-1]

"""
Generic async CRUD base repository.
All collection-specific repos inherit from this class.
"""
from datetime import datetime, UTC
from typing import Any, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from app.utils.id_utils import to_object_id

T = TypeVar("T")


class BaseRepository:
    """
    Provides common CRUD operations as async methods.
    Subclasses set `collection_name` and call super().__init__(db).
    """

    collection_name: str = ""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._col: AsyncIOMotorCollection = db[self.collection_name]

    async def insert_one(self, document: dict[str, Any]) -> str:
        """Insert a document with default audit and soft delete fields, and return its string id."""
        if "created_at" not in document:
            document["created_at"] = datetime.now(UTC)
        if "updated_at" not in document:
            document["updated_at"] = datetime.now(UTC)
        if "is_deleted" not in document:
            document["is_deleted"] = False
            
        result: InsertOneResult = await self._col.insert_one(document)
        return str(result.inserted_id)

    async def find_by_id(self, id_str: str, include_deleted: bool = False) -> dict[str, Any] | None:
        """Find a single document by string ObjectId."""
        oid = to_object_id(id_str)
        query: dict[str, Any] = {"_id": oid}
        if not include_deleted:
            query["is_deleted"] = {"$ne": True}
            
        doc = await self._col.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def find_one(self, query: dict[str, Any], include_deleted: bool = False) -> dict[str, Any] | None:
        """Find a single document matching query."""
        adjusted_query = dict(query)
        if not include_deleted:
            adjusted_query["is_deleted"] = {"$ne": True}
            
        doc = await self._col.find_one(adjusted_query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def find_many(
        self,
        query: dict[str, Any],
        sort: list[tuple[str, int]] | None = None,
        limit: int = 0,
        include_deleted: bool = False,
    ) -> list[dict[str, Any]]:
        """Find multiple documents."""
        adjusted_query = dict(query)
        if not include_deleted:
            adjusted_query["is_deleted"] = {"$ne": True}
            
        cursor = self._col.find(adjusted_query)
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        docs = await cursor.to_list(length=None)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    async def update_one(
        self, id_str: str, update: dict[str, Any]
    ) -> UpdateResult:
        """Update a document by id, automatically updating the updated_at audit timestamp."""
        oid = to_object_id(id_str)
        
        # Ensure updated_at audit field is refreshed on every update
        if "$set" not in update:
            update["$set"] = {}
        update["$set"]["updated_at"] = datetime.now(UTC)
        
        return await self._col.update_one({"_id": oid}, update)

    async def soft_delete(self, id_str: str) -> UpdateResult:
        """Soft delete a document by setting is_deleted flag."""
        return await self.update_one(
            id_str,
            {
                "$set": {
                    "is_deleted": True,
                    "deleted_at": datetime.now(UTC)
                }
            }
        )

    async def delete_one(self, id_str: str) -> DeleteResult:
        """Hard delete a document by id."""
        oid = to_object_id(id_str)
        return await self._col.delete_one({"_id": oid})

    async def count(self, query: dict[str, Any] | None = None, include_deleted: bool = False) -> int:
        adjusted_query = dict(query or {})
        if not include_deleted:
            adjusted_query["is_deleted"] = {"$ne": True}
        return await self._col.count_documents(adjusted_query)

    async def aggregate(self, pipeline: list[dict]) -> list[dict[str, Any]]:
        docs = await self._col.aggregate(pipeline).to_list(length=None)
        for doc in docs:
            if "_id" in doc and isinstance(doc["_id"], ObjectId):
                doc["_id"] = str(doc["_id"])
        return docs

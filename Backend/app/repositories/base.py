"""
Generic async CRUD base repository.
All collection-specific repos inherit from this class.
"""
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
        """Insert a document and return its string id."""
        result: InsertOneResult = await self._col.insert_one(document)
        return str(result.inserted_id)

    async def find_by_id(self, id_str: str) -> dict[str, Any] | None:
        """Find a single document by string ObjectId."""
        oid = to_object_id(id_str)
        doc = await self._col.find_one({"_id": oid})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        """Find a single document matching query."""
        doc = await self._col.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def find_many(
        self,
        query: dict[str, Any],
        sort: list[tuple[str, int]] | None = None,
        limit: int = 0,
    ) -> list[dict[str, Any]]:
        """Find multiple documents."""
        cursor = self._col.find(query)
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
        """Update a document by id."""
        oid = to_object_id(id_str)
        return await self._col.update_one({"_id": oid}, update)

    async def delete_one(self, id_str: str) -> DeleteResult:
        """Delete a document by id."""
        oid = to_object_id(id_str)
        return await self._col.delete_one({"_id": oid})

    async def count(self, query: dict[str, Any] | None = None) -> int:
        return await self._col.count_documents(query or {})

    async def aggregate(self, pipeline: list[dict]) -> list[dict[str, Any]]:
        docs = await self._col.aggregate(pipeline).to_list(length=None)
        for doc in docs:
            if "_id" in doc and isinstance(doc["_id"], ObjectId):
                doc["_id"] = str(doc["_id"])
        return docs

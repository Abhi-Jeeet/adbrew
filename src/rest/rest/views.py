import json
import logging
import os

from pymongo import MongoClient
from urllib.parse import parse_qs

from bson import ObjectId
from django.http.multipartparser import MultiPartParserError
from pymongo import MongoClient
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------

mongo_uri = "mongodb://" + os.environ["MONGO_HOST"] + ":" + os.environ["MONGO_PORT"]
db = MongoClient(mongo_uri)["test_db"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _serialize_todo(todo: dict) -> dict:
    """Convert a MongoDB document to a JSON-serializable dict."""
    return {
        "id": str(todo["_id"]),
        "description": todo.get("description", ""),
    }


def _extract_description(request) -> str:
    """
    Robustly extract the todo description from any request format:
    1. DRF request.data (handles JSONParser, FormParser, MultiPartParser)
    2. Django request.POST
    3. Query params (?description=...)
    4. Raw request.body fallback (in case client sent malformed Content-Type)
    Supports keys: 'description', 'todo', 'title', 'text', 'task', 'name'.
    """
    candidate_keys = ("description", "todo", "title", "text", "task", "name")

    # 1. DRF request.data
    try:
        data = request.data
        if isinstance(data, dict):
            for key in candidate_keys:
                val = data.get(key)
                if val is not None and str(val).strip():
                    return str(val).strip()
        elif isinstance(data, str) and data.strip():
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict):
                    for key in candidate_keys:
                        val = parsed.get(key)
                        if val is not None and str(val).strip():
                            return str(val).strip()
                elif isinstance(parsed, str):
                    return parsed.strip()
            except Exception:
                return data.strip()
    except Exception:
        pass

    # 2. Django request.POST (for form submissions)
    try:
        for key in candidate_keys:
            val = request.POST.get(key)
            if val is not None and str(val).strip():
                return str(val).strip()
    except Exception:
        pass

    # 3. Query parameters (e.g. /todos?description=...)
    try:
        for key in candidate_keys:
            val = request.query_params.get(key)
            if val is not None and str(val).strip():
                return str(val).strip()
    except Exception:
        pass

    # 4. Fallback: inspect raw body (handles clients that set bad headers)
    try:
        raw_text = request.body.decode("utf-8", errors="ignore").strip()
        if raw_text:
            try:
                parsed = json.loads(raw_text)
                if isinstance(parsed, dict):
                    for key in candidate_keys:
                        val = parsed.get(key)
                        if val is not None and str(val).strip():
                            return str(val).strip()
                elif isinstance(parsed, str):
                    return parsed.strip()
            except Exception:
                pass

            qs = parse_qs(raw_text)
            for key in candidate_keys:
                vals = qs.get(key)
                if vals and vals[0].strip():
                    return vals[0].strip()

            if not raw_text.startswith("{") and not raw_text.startswith("<"):
                return raw_text
    except Exception:
        pass

    return ""


# ---------------------------------------------------------------------------
# Repository – all Mongo interactions are isolated here (Single Responsibility)
# ---------------------------------------------------------------------------


class TodoRepository:
    """Thin abstraction layer over the MongoDB `todos` collection."""

    COLLECTION = "todos"

    def __init__(self, database):
        self._collection = database[self.COLLECTION]

    def get_all(self) -> list:
        """Return every todo document as a list of serializable dicts."""
        return [_serialize_todo(doc) for doc in self._collection.find()]

    def create(self, description: str) -> dict:
        """Insert a new todo and return the created document."""
        if not description or not description.strip():
            raise ValueError("description must be a non-empty string")
        result = self._collection.insert_one({"description": description.strip()})
        return _serialize_todo(
            self._collection.find_one({"_id": result.inserted_id})
        )


# Singleton repository – reuses the existing `db` connection
todo_repo = TodoRepository(db)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


class TodoListView(APIView):
    """
    GET  /todos  – List all todos stored in MongoDB.
    POST /todos  – Create a new todo in MongoDB.
    Supports application/json, application/x-www-form-urlencoded, and multipart/form-data.
    """

    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get(self, request):
        try:
            todos = todo_repo.get_all()
            return Response({"todos": todos}, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.exception("Failed to fetch todos")
            return Response(
                {"error": "Failed to fetch todos", "detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            description = _extract_description(request)
            todo = todo_repo.create(description)
            return Response({"todo": todo}, status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response(
                {
                    "error": str(exc),
                    "help": (
                        "Provide a non-empty 'description' field. "
                        "Accepted Content-Types: application/json, "
                        "application/x-www-form-urlencoded, or multipart/form-data."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.exception("Failed to create todo")
            return Response(
                {"error": "Failed to create todo", "detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

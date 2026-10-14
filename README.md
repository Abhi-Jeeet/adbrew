# Adbrew Full-Stack Coding Assessment

A full-stack Todo application built with **React (Hooks)**, **Django REST Framework (PyMongo)**, and **MongoDB**, fully orchestrated with **Docker Compose**.

---

## 🏗️ Architecture & Services

The application runs in three containerized services connected over an internal Docker network:

| Service | Technology | Port | Description |
|---|---|---|---|
| **`app`** | React 18, React Scripts 5.0.1 | `3000` | Frontend client utilizing pure React Hooks |
| **`api`** | Django 3.0, Django REST Framework | `8000` | REST API communicating directly with MongoDB |
| **`mongo`** | MongoDB 6 (Official Image) | `27017` | Persistent document database |

---

## 🛠️ Implementation Summary & What Was Done

### 1. Docker & Dependency Modernization
To resolve legacy dependency deprecations and build failures:
- **MongoDB Service:** Switched the `mongo` service in `docker-compose.yml` to the official `mongo:6` Docker Hub image, removing broken legacy Debian Buster APT repos from the Dockerfile.
- **Python Tooling:** Replaced deprecated `easy_install` invocations with modern `pip install --upgrade pip`.
- **Cleaned Requirements:** Replaced an 84-package dependency list containing yanked PyPI packages (e.g. `celery==5.0.5`) with only the 6 packages actually required (`Django`, `djangorestframework`, `django-cors-headers`, `pymongo`, `asgiref`, `sqlparse`).
- **Node.js 18 Compatibility:** Upgraded `react-scripts` from `4.0.1` to `5.0.1` in `src/app/package.json` to resolve `ERR_PACKAGE_PATH_NOT_EXPORTED` caused by Node 18's strict package export rules.

### 2. Backend Implementation (`src/rest/rest/`)
- **Repository Pattern (`TodoRepository`):** Applied the Single Responsibility Principle by decoupling MongoDB data access from Django views (`views.py`).
- **Direct PyMongo Integration:** Avoided Django ORM and SQLite as required; connected directly to `test_db.todos` with ObjectId serialization helper (`_serialize_todo`).
- **Flexible Route & Trailing Slash Handling:** Set `APPEND_SLASH = False` in `settings.py` and used regex routing `re_path(r'^todos/?$', ...)` so both `/todos` and `/todos/` accept GET and POST requests without dropping payload data.
- **Multi-Format Ingestion:** Declared DRF parsers (`JSONParser`, `FormParser`, `MultiPartParser`) and implemented a multi-tiered extractor (`_extract_description`) supporting `application/json`, `application/x-www-form-urlencoded`, and `multipart/form-data`.
- **Status Codes & Validation:** Returns `201 Created` on creation, `200 OK` on list, `400 Bad Request` with actionable help on invalid input, and `500` with server logging on error.

### 3. Frontend Implementation (`src/app/src/`)
- **Strict React Hooks (Zero Class Components):** Completely hook-driven architecture using `useState`, `useEffect`, and `useCallback`.
- **Three-Tier Modular Architecture:**
  1. `api/todoApi.js`: Dedicated HTTP service layer encapsulating all `fetch()` calls.
  2. `hooks/useTodos.js`: Custom hook managing state (`todos`, `loading`, `error`), initial data fetching, and optimistic re-fetching after creating a todo.
  3. `components/TodoForm.js` & `components/TodoList.js`: Focused presentational components featuring controlled inputs, disable-while-submitting states, and user feedback.

### 4. Database Persistence & Repository Hygiene
- **Host Persistence:** Mounted host path `${ADBREW_CODEBASE_PATH}/db/` to container path `/data/db`, ensuring data persists across container restarts via MongoDB's WiredTiger engine.
- **Clean Git Tracking:** Added a root `.gitignore` to prevent runtime MongoDB binaries (`src/db/`), bytecode caches (`__pycache__`), and `node_modules` from polluting the Git repository.

---

## 🚀 Quickstart & Setup

### 1. Set the Codebase Path Environment Variable
From the root of this repository:
```bash
export ADBREW_CODEBASE_PATH="$(pwd)/src"
```

### 2. Build and Start the Containers
```bash
docker-compose up -d --build
```

### 3. Verify Containers
```bash
docker ps
```
All three containers (`api`, `app`, `mongo`) should be running.

### 4. Access the Application
- **Frontend App:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000/todos](http://localhost:8000/todos)

---

## 🧪 Testing the API

```bash
# 1. Fetch all todos
curl -s http://localhost:8000/todos | python3 -m json.tool

# 2. Create a todo (JSON)
curl -i -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"description": "Learn Docker and React Hooks"}'

# 3. Create a todo (URL-encoded form)
curl -i -X POST http://localhost:8000/todos \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "description=Review code architecture"

# 4. Create a todo (Multipart form-data)
curl -i -X POST http://localhost:8000/todos \
  -F "description=Ship solution"
```

---

## 🛑 Stopping the Containers
```bash
docker-compose down
```
*(Your database records will persist in `src/db/` for the next time you run `docker-compose up -d`)*

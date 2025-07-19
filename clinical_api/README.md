# Clinical Documentation API

A FastAPI-based backend for clinical documentation with ICD-10 code search capabilities.

---

## 🚀 Features

- ICD-10 code search by keyword
- Auto-seeded database with sample codes
- CORS support for frontend integration (React, Vite, etc.)
- Health check endpoint

---

## 🧱 Tech Stack

- **FastAPI** for the web framework
- **SQLite** for the database
- **Pydantic** for data validation
- **Uvicorn** as the ASGI server

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the API

Run from the project root using uvicorn:

```bash
uvicorn main:app --reload

---

## 🛠 Project Structure

```
clinical_api/
├── main.py                  # API entrypoint, mounts routes and starts the app
├── config.py                # App configuration (CORS, DB path, API metadata, etc.)
├── requirements.txt         # List of required Python packages
├── models/
│   └── icd10.py             # Pydantic models (e.g., ICD10Code, ICD10SearchResponse)
├── database/
│   ├── connection.py        # Returns a SQLite DB connection
│   ├── models.py            # Table creation logic (e.g., create_tables)
│   └── seed_data.py         # Inserts initial sample ICD-10 data
├── services/
│   └── icd10_service.py     # Business logic to search ICD-10 codes
├── api/
│   └── routes/
│       ├── health.py        # GET /api/health - health check route
│       └── icd10.py         # GET /api/icd10/?q=keyword - search ICD-10 codes
└── utils/                   # (Optional) Common helpers if needed
```

---

## 🔍 Example API Requests

### Health Check

```http
GET http://localhost:8000/api/health
```

### ICD-10 Code Search

```http
GET http://localhost:8000/api/icd10?q=pneumonia&limit=5
```

---

## 📝 API Documentation

Once the server is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

---
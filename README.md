# Cloud HW1 - User Management API

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

A User Management REST API built with FastAPI, featuring user registration, authentication, role-based filtering, and pagination.

## Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI |
| **ORM** | SQLModel |
| **Database** | PostgreSQL 16 |
| **Password Hashing** | bcrypt |
| **Migrations** | Alembic |
| **Pagination** | fastapi-pagination |
| **Server** | Uvicorn |
| **Containerization** | Docker Compose |

## Quick Start

### Prerequisites

- Python 3.x
- Docker & Docker Compose

### Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Then edit `.env` with your database credentials.

### Automated Setup

```bash
python setup.py
```

This will install dependencies, start PostgreSQL, run migrations, and launch the server.

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL
docker-compose up -d

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host localhost --port 8000
```

### API Documentation

Once running, access the interactive API docs at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Data Population

To initialize the database with sample users, visit the root endpoint:

```
GET http://localhost:8000/
```

This will automatically populate the database with sample data on first access.

## Project Structure

```
cloud-hw1/
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── database.py       # Database connection setup
│   ├── autogen.py        # Sample data initialization
│   ├── auth/
│   │   └── utils.py      # Authentication & password utilities
│   ├── models/
│   │   ├── user.py       # User SQLModel
│   │   └── consts.py     # Constants (timezone, enums)
│   └── routers/
│       └── users.py      # User API endpoints
├── migrations/
│   └── versions/         # Alembic migration files
├── docker-compose.yml    # PostgreSQL container config
├── requirements.txt      # Python dependencies
├── setup.py              # Automated setup script
└── alembic.ini           # Alembic configuration
```

## Security

- **Password Hashing**: All passwords are hashed using bcrypt with salt
- **Password Requirements**:
  - Minimum 3 characters
  - At least one digit
  - At least one lowercase letter
  - At least one uppercase letter
- **Response Safety**: Passwords are excluded from all API responses

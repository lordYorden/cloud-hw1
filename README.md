# Cloud HW1 - User Management API

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Python Recommended](https://img.shields.io/badge/Recommended-3.13.x-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![uv](https://img.shields.io/badge/uv-DE5FE9?logo=uv&logoColor=white)

A User Management REST API built with FastAPI, featuring user registration, authentication, role-based filtering, and pagination.

## Tech Stack

| Category                   | Technology              |
| -------------------------- | ----------------------- |
| **Framework**        | FastAPI                 |
| **ORM**              | SQLModel                |
| **Database**         | PostgreSQL 16           |
| **Password Hashing** | bcrypt                  |
| **Migrations**       | Alembic                 |
| **Pagination**       | fastapi-pagination      |
| **Server**           | Uvicorn                 |
| **Package Manager**  | uv (recommended) or pip |
| **Containerization** | Docker Compose          |

## Quick Start

### Prerequisites

- Python 3.9+ (recommended: 3.13.x)
  - *Minimum 3.9 required due to the `zoneinfo` standard library module*
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

> **Note**: The setup script automatically detects and uses [uv](https://docs.astral.sh/uv/) if installed, falling back to pip otherwise.

### Manual Setup

#### Using uv (recommended)

```bash
# Install dependencies and create .venv
uv sync

# Start PostgreSQL
docker-compose up -d

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --host localhost --port 8000
```

#### Using pip

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

### Running After Setup

After initial setup, PostgreSQL runs automatically so just start the server:

#### Using uv

```bash
uv run uvicorn app.main:app --host localhost --port 8000
```

#### Using pip

```bash
uvicorn app.main:app --host localhost --port 8000
```

> **Note**: If PostgreSQL isn't running, start it with `docker-compose up -d`

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

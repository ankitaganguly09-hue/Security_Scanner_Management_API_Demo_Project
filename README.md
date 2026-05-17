# Security_Scanner_Management_API_Demo_Project

A FastAPI-based demo project for security scan management with PostgreSQL persistence, user registration, JWT authentication, and Swagger OAuth2 authorization.

## Key Features

- CRUD operations for security scan records
- PostgreSQL database integration using SQLAlchemy
- User registration with hashed passwords using Passlib + bcrypt
- JWT-based authentication for protected endpoints
- Swagger UI authorization via OAuth2 password flow
- Hidden token endpoint for secure login handling

## Architecture Overview

- `app/main.py` - FastAPI application and route definitions
- `app/auth/authentication.py` - JWT generation, verification, and current-user dependency
- `app/database/connection.py` - SQLAlchemy database connection and session management
- `app/models/database_model.py` - SQLAlchemy models for `Scan` and `User`
- `app/schemas/pydantic_schema.py` - Pydantic request/response models for validation

## Installation

1. Create and activate a virtual environment:

```powershell
python -m venv myenv
myenv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Configure PostgreSQL connection in `app/database/connection.py` if needed.

## Running the App

```powershell
myenv\Scripts\python -m uvicorn app.main:app --reload
```

Open Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

## Authentication Flow

- Users register via `POST /users/` with a username, email, and password.
- Passwords are hashed using `passlib` with the `bcrypt` algorithm.
- Swagger UI uses the **Authorize** button to obtain a JWT token from the hidden `/token` endpoint.
- Protected API routes, such as `GET /`, require a valid JWT token.

## How It Works (Interview / Resume Friendly)

- Built a REST API using **FastAPI** and **SQLAlchemy** to manage security scan records.
- Implemented secure user registration with hashed passwords using **Passlib + bcrypt**.
- Added JWT-based authentication so only authorized users can access protected data.
- Integrated Swagger UI OAuth2 flow so login happens through the **Authorize** button instead of a visible login route.
- Used PostgreSQL as the persistence layer and handled database session management cleanly with dependency injection.

## Example Resume Bullet

- Developed a FastAPI-based security scanner management API with PostgreSQL persistence, user registration, hashed password security, JWT authentication, and Swagger OAuth2 login.

## Notes

- The JWT `SECRET_KEY` is currently read from environment variables, with a default fallback for local testing.
- The `/token` endpoint is intentionally hidden from API docs and leveraged only by Swagger UI for authorization.

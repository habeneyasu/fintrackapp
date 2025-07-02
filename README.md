# fintrackapp
Personal Finance Tracker API
A RESTful financial management system built with FastAPI and PostgreSQL

📌 Overview
A production-grade API for tracking incomes, expenses, and savings goals with:

JWT Authentication (OAuth2 password flow)

Multi-Currency Support (ETB, USD, etc.)

Recurring Transaction Detection (Monthly/Weekly/One-time)

Budget Analytics (Category-wise spending limits)

Automated Savings Progress (Target amount tracking)

🛠 Tech Stack
Component	Technology
Framework	FastAPI 0.95+
Database	PostgreSQL 15 (SQLAlchemy 2.0 ORM)
Auth	JWT (HS256)
Testing	pytest (90% coverage)
Infrastructure	Docker + Docker Compose
CI/CD	GitHub Actions

📂 Project Structure
app/
├── core/               # Config, security, middleware
├── db/                 # PostgreSQL models & migrations
├── features/           # Domain-driven modules
│   ├── users/          # Auth and profiles
│   ├── incomes/        # Salary, freelance tracking
│   ├── expenses/       # Categorized spending
│   └── savings/        # Goal progress automation
├── api/                # Versioned API routers
└── tests/              # Unit + integration tests

🚀 Installation
Prerequisites
Python 3.11+

PostgreSQL 15+

Docker (optional)

Local Setup

1.Clone the repo:
    git clone https://github.com/habeneyasu/fintrackapp
    cd fintrackapp

2.Configure environment:
    cp .env.example .env  # Update PostgreSQL credentials
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

3. Run migrations:
    alembic upgrade head
    
4.Start the server:
    uvicorn main:app --reload 

Docker Setup:
    docker-compose up --build
📚 API Documentation
Interactive documentation available at:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

    Sample Endpoints:

    Endpoint	Method	Description
    /api/v1/incomes	POST	Log new income
    /api/v1/expenses	GET	List all expenses
    /api/v1/savings/goals	PUT	Update savings target
🧪 Testing
Run the test suite with coverage:
    pytest tests/ --cov=app --cov-report=term-missing

Tests include:

    JWT auth flow validation
    Transaction CRUD operations
    Budget limit enforcement

🔧 CI/CD Pipeline
    Automated tests on pull requests
    Docker image build on main branch merges
    PostgreSQL health checks in staging
📜 License
MIT License © 2025 Haben Eyasu

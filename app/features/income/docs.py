from enum import Enum
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Financial Tracker API",
        version="1.0.0",
        description="API for tracking personal finances",
        routes=app.routes,
    )
    
    # Add enum examples to schema
    openapi_schema["components"]["schemas"]["IncomeSource"] = {
        "title": "IncomeSource",
        "description": "The source of the income",
        "enum": ["Salary", "Freelance", "Dividend", "Bonus", "Investment", "Other"],
        "type": "string"
    }
    
    openapi_schema["components"]["schemas"]["IncomeFrequency"] = {
        "title": "IncomeFrequency",
        "description": "How often the income occurs",
        "enum": ["Monthly", "Weekly", "Biweekly", "One-time"],
        "type": "string"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, education, goal, recommendations, portfolio
from models.audit_log import AuditLog  # Import for Alembic migration tracking

app = FastAPI(title="InvestEase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(goal.router)
app.include_router(education.router)
app.include_router(recommendations.router)
app.include_router(portfolio.router)


@app.get("/")
async def root():
    return {"status": "InvestEase API running"}
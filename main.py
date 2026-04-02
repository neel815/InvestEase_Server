from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, education, goal, recommendations, portfolio, explore
from models.audit_log import AuditLog  # Import for Alembic migration tracking
from core.dependenices import get_current_user

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
app.include_router(explore.router)


@app.get("/")
async def root():
    return {"status": "InvestEase API running"}


@app.get("/debug/test-auth")
async def test_auth(user_id: str = Depends(get_current_user)):
    """Test endpoint to verify authentication is working"""
    return {"status": "authenticated", "user_id": user_id}


@app.get("/debug/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {"status": "CORS working", "message": "If you see this, CORS is configured correctly"}
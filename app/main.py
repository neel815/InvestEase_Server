from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path so we can import core, db, models, routers, schemas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers import auth, education, goal, recommendations

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

@app.get("/")
async def root():
    return {"status": "InvestEase API running"}

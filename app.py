from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import poker_range_recommender as pr

app = FastAPI(
    title="Preflop Advisor API",
    version="1.0.0",
    description="Open / Shove / 3-Bet recommendations based on your range book."
)

# CORS – פתח לזמן בדיקה; אחר כך אפשר לצמצם ל-["https://thenapo.github.io"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendBody(BaseModel):
    hand: str
    position: str = Field(..., description="UTG/MP/HJ/CO/BTN/SB/BB")
    stack: float
    context: str = Field("auto", pattern="^(auto|open|shove)$")

class VsOpenBody(BaseModel):
    hand: str
    hero_pos: str = Field(..., description="UTG/MP/HJ/CO/BTN/SB/BB")
    opener_pos: str = Field(..., description="UTG/MP/HJ/CO/BTN")
    stack: float

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/recommend")
def recommend(body: RecommendBody):
    return pr.recommend_action(body.hand, body.position, body.stack, body.context)

@app.post("/vs-open")
def vs_open(body: VsOpenBody):
    return pr.recommend_vs_open(body.hand, body.hero_pos, body.opener_pos, body.stack)

@app.get("/")
def root():
    return {"service": "Preflop Advisor API", "docs": "/docs", "health": "/health"}

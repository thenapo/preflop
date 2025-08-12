
import os
from fastapi import FastAPI
from pydantic import BaseModel, Field
import poker_range_recommender as pr

app = FastAPI(
    title="Preflop Advisor API",
    version="0.1.0",
    description="Open / Shove / 3-Bet recommendations based on your range book."
)

class RecommendBody(BaseModel):
    hand: str = Field(..., description="e.g., AKs, AJo, 22, AhKh")
    position: str = Field(..., description="UTG/MP/HJ/CO/BTN/SB/BB")
    stack: float = Field(..., description="Stack in big blinds")
    context: str = Field("auto", pattern="^(auto|open|shove)$", description="auto|open|shove")

class VsOpenBody(BaseModel):
    hand: str
    hero_pos: str = Field(..., description="Your position: UTG/MP/HJ/CO/BTN/SB/BB")
    opener_pos: str = Field(..., description="Opener position: UTG/MP/HJ/CO/BTN")
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

# Convenience root
@app.get("/")
def root():
    return {"service": "Preflop Advisor API", "docs": "/docs", "health": "/health"}

# app.py
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from poker_range_recommender import (
    open_recommendation,
    vs_open_recommendation
)

app = FastAPI(title="Preflop Advisor API", version="0.1.0")

# CORS (לצרכי GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendBody(BaseModel):
    hand: str = Field(..., description="e.g. AJo / 22 / AKs")
    position: str = Field(..., description="UTG/MP/HJ/CO/BTN/SB/BB")
    stack: float = Field(..., description="Stack in BB")
    context: str = Field("auto", pattern="^(auto|open|shove)$")

class VsOpenBody(BaseModel):
    hand: str
    hero_pos: str
    opener_pos: str
    stack: float

@app.get("/")
def root():
    return "Preflop Advisor API"

@app.get("/health")
def health():
    return "ok"

@app.post("/recommend")
def recommend(body: RecommendBody):
    try:
        decision, why = open_recommendation(body.hand.strip(), body.position.strip().upper(), body.stack, body.context)
        return {"decision": decision, "why": why}
    except Exception as e:
        return {"error": str(e)}

@app.post("/vs-open")
def vs_open(body: VsOpenBody):
    try:
        decision, sizing, why = vs_open_recommendation(
            body.hand.strip(),
            body.hero_pos.strip().upper(),
            body.opener_pos.strip().upper(),
            body.stack
        )
        return {"decision": decision, "sizing": sizing, "why": why}
    except Exception as e:
        return {"error": str(e)}

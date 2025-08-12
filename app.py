# app.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from poker_range_recommender import open_recommendation, vs_open_recommendation

app = FastAPI(title="Preflop Advisor API", version="0.1.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendBody(BaseModel):
    hand: str
    position: str
    stack: float
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
        decision, sizing, why = open_recommendation(body.hand, body.position, body.stack, body.context)
        return {"decision": decision, "sizing": sizing, "why": why}
    except Exception as e:
        return {"error": str(e)}

@app.post("/vs-open")
def vs_open(body: VsOpenBody):
    try:
        decision, sizing, why = vs_open_recommendation(body.hand, body.hero_pos, body.opener_pos, body.stack)
        return {"decision": decision, "sizing": sizing, "why": why}
    except Exception as e:
        return {"error": str(e)}

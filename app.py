from fastapi import FastAPI
from pydantic import BaseModel
from poker_range_recommender import get_recommendation, recommend_vs_open
from fastapi.middleware.cors import CORSMiddleware

# יצירת האפליקציה
app = FastAPI(
    title="Preflop Advisor API",
    version="1.0.0",
    description="Open / Shove / 3-Bet recommendations based on your range book."
)

# הגדרת CORS - זמנית אפשר לאפשר לכולם עם "*", ואח"כ לצמצם לכתובת ה-GitHub Pages שלך
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://thenapo.github.io",           # הדומיין שלך ב-GitHub Pages
        "https://thenapo.github.io/preflop"    # תת-תיקייה אם צריך
        # "*",  # ← אם תרצה לאפשר לכולם לבדיקה מהירה
    ],
    allow_credentials=True,
    allow_methods=["*"],  # מאפשר את כל סוגי הבקשות (GET, POST, OPTIONS)
    allow_headers=["*"],  # מאפשר כל כותרות (Headers)
)

# מודלים לנתונים נכנסים
class RecommendRequest(BaseModel):
    hand: str
    position: str
    stack: int

class VsOpenRequest(BaseModel):
    hand: str
    position: str
    open_position: str
    stack: int

# בדיקת חיות השרת
@app.get("/health")
async def health():
    return {"status": "ok"}

# המלצה רגילה
@app.post("/recommend")
async def recommend(req: RecommendRequest):
    return {"recommendation": get_recommendation(req.hand, req.position, req.stack)}

# המלצה נגד פתיחה
@app.post("/vs-open")
async def vs_open(req: VsOpenRequest):
    return {"recommendation": recommend_vs_open(req.hand, req.position, req.open_position, req.stack)}

# דף בית (לא חובה)
@app.get("/")
async def root():
    return {"message": "Preflop Advisor API is running"}


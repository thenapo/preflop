# poker_range_recommender.py
# -*- coding: utf-8 -*-

from typing import Tuple, Dict, List

# -------------------- Hand utils --------------------

def is_pair(h: str) -> bool:
    return len(h) >= 2 and h[0] == h[1]

def rank_order(ch: str) -> int:
    order = "AKQJT98765432"  # lower index = stronger
    return order.index(ch)

def pair_ge(hand: str, floor_pair: str) -> bool:
    return is_pair(hand) and is_pair(floor_pair) and rank_order(hand[0]) <= rank_order(floor_pair[0])

def x_plus_match(hand: str, spec: str) -> bool:
    """
    Supports:
      - '22+' (pairs >=)
      - 'A2s+' / 'A8o+' (same first rank + suitedness; second rank >= spec's)
      - exacts like 'KQo','QJs','JTs','T9s'
    """
    spec = spec.strip()
    if not spec:
        return False
    if spec.endswith('+'):
        core = spec[:-1]
        if len(core) == 2 and core[0] == core[1]:
            return pair_ge(hand, core)
        if len(core) == 3:
            r1, r2, so = core[0], core[1], core[2]
            if len(hand) != 3:
                return False
            h1, h2, hso = hand[0], hand[1], hand[2]
            if h1 != r1 or hso != so:
                return False
            return rank_order(h2) <= rank_order(r2)
        return False
    else:
        return hand == spec

def hand_in_any(hand: str, specs: List[str]) -> bool:
    return any(x_plus_match(hand, s) for s in specs)

# -------------------- Position helpers --------------------

def map_pos_class(position: str) -> str:
    """
    Map table position to shove-class used in the book: EP / MP / LP / SB
    """
    p = position.strip().upper()
    if p == "UTG":
        return "EP"
    if p == "MP":
        return "MP"
    if p in ("HJ", "CO", "BTN"):
        return "LP"
    if p == "SB":
        return "SB"
    return p  # BB, etc.

# -------------------- Shove ranges (10/15/20BB) --------------------

SHOVE_RANGES: Dict[int, Dict[str, List[str]]] = {
    10: {
        "EP": ['44+', 'A5s+', 'ATo+', 'KQs'],
        "MP": ['A7s+', 'ATo+', 'KJs+', 'QJs', '87s+'],
        "LP": ['K3s+', 'Q6s+', 'J8s+', '65s+', 'KTo+'],
        "SB": ['22+', 'A2s+', 'K5s+', 'Q8s+', 'J9s+'],
    },
    15: {
        "EP": ['33+', 'A3s+', 'A9o+', 'KQs'],
        "MP": ['33+', 'A3s+', 'A9o+', 'KTs+', 'QTs+', 'JTs'],
        "LP": ['K5s+', 'Q8s+', '76s+', 'K9o+'],
        "SB": ['22+', 'A2s+', 'K7s+', 'Q9s+', 'JTs'],
    },
    20: {
        "EP": ['22+', 'A2s+', 'A8o+', 'KJs+'],
        "MP": ['22+', 'A2s+', 'A8o+', 'KTs+', 'QTs+'],
        "LP": ['A5o+', 'K8s+', 'Q9s+', '87s+'],
        "SB": ['22+', 'A2s+', 'K9s+', 'QTs+'],
    }
}

def shove_bucket(stack: float) -> int:
    if stack <= 12:
        return 10
    if stack <= 17:
        return 15
    return 20

# -------------------- Opening snapshots (100/50/30/15BB) --------------------

OPEN_100 = {
    "UTG": ['22+', 'A2s+', 'AJo+', 'KQo', 'KJs+', 'QJs'],
    "MP":  ['22+', 'A2s+', 'ATs+', 'ATo+', 'KTs+', 'QTs+', 'JTs'],
    "HJ":  ['22+', 'A2s+', 'A9o+', 'K9s+', 'Q9s+', 'J9s+', 'T9s'],
    "CO":  ['22+', 'A2s+', 'A8o+', 'K8s+', 'Q8s+', 'J8s+', '98s', '54s+'],
    "BTN": ['22+', 'A2s+', 'A2o+', 'K2s+', 'Q2s+', 'J2s+', 'T9s', '98s', '87s', '76s', '65s', '54s'],
    "SB":  [],  # לא הוגדר במפורש בטבלת הפתיחות
}
OPEN_50 = OPEN_100
OPEN_30 = {
    "UTG": ['22+', 'A2s+', 'ATs+', 'AQo', 'KQs'],
    "MP":  ['22+', 'A2s+', 'ATs+', 'ATo+', 'KTs+', 'QTs+', 'JTs'],
    "HJ":  OPEN_100["HJ"],
    "CO":  OPEN_100["CO"],
    "BTN": OPEN_100["BTN"],
    "SB":  [],
}
OPEN_15 = {
    "UTG": ['66+', 'ATs+', 'AJ+', 'KQs'],
    "MP":  ['55+', 'ATs+', 'AJ+', 'KQo'],
    "HJ":  ['44+', 'ATs+', 'AJ+', 'KTs+'],
    "CO":  ['22+', 'A2s+', 'A9o+', 'K9s+', 'Q9s+'],
    "BTN": OPEN_100["BTN"],
    "SB":  [],
}

def open_bucket(stack: float) -> str:
    if stack >= 60:
        return "OPEN_100"
    if stack >= 40:
        return "OPEN_50"
    if stack >= 20:
        return "OPEN_30"
    return "OPEN_15"

OPEN_BY_BUCKET = {
    "OPEN_100": OPEN_100,
    "OPEN_50":  OPEN_50,
    "OPEN_30":  OPEN_30,
    "OPEN_15":  OPEN_15,
}

# -------------------- Sizing helpers --------------------

def threebet_sizing_by_stack_ip(stack: float) -> str:
    if stack >= 100:
        return "3x רייז של הפותח"
    if stack >= 50:
        return "2.7x–3.0x רייז של הפותח"
    if stack >= 30:
        return "2.3x–2.7x רייז של הפותח"
    return "דחיפה/שורט בהתאם לטווחים"

def open_raise_sizing(stack: float, position: str) -> str:
    """
    קובעת גודל פתיחה מומלץ (לא דחיפה) לפי עומק ועמדה.
    פשוט ושמרני, מתאים לטורנירים מודרניים.
    """
    p = position.upper()
    cls = map_pos_class(p)
    if p == "SB":
        # SB מול BB בדרך כלל גדול יותר
        if stack >= 40: return "2.5x–3.0x (SB vs BB)"
        if stack >= 20: return "2.3x–2.7x (SB vs BB)"
        return "2.2x–2.5x (SB vs BB)"
    if cls == "EP":
        if stack >= 60: return "2.3x–2.5x"
        if stack >= 40: return "2.2x–2.4x"
        return "~2.1x–2.3x"
    # MP / LP / BTN
    if stack >= 60: return "2.0x–2.3x"
    if stack >= 40: return "~2.0x–2.2x"
    return "~2.0x (מינ-רייז)"

# -------------------- Public API --------------------

VALID_OPEN_POS = {"UTG", "MP", "HJ", "CO", "BTN", "SB"}  # BB אינו פותח

def open_recommendation(hand: str, position: str, stack: float, context: str = "auto") -> Tuple[str, str, str]:
    """
    Decide Open-Raise / Shove / Fold from an unopened pot.
    Returns (decision, sizing, why).
    """
    h = hand.strip()
    pos = position.strip().upper()

    if pos not in VALID_OPEN_POS:
        raise ValueError("BB אינו פותח קופה לא פתוחה. בחר עמדה אחרת (UTG/MP/HJ/CO/BTN/SB).")

    cls = map_pos_class(pos)

    # 1) Shove model (short) — only if shallow or user forced 'shove'
    if context == "shove" or stack <= 20:
        bucket = shove_bucket(stack)
        specs_map = SHOVE_RANGES.get(bucket, {})
        if cls in specs_map:
            specs = specs_map[cls]
            if hand_in_any(h, specs):
                return ("Shove (All-in)", "Jam", f"שורט {bucket}BB, {pos} ({cls}). בטווח הדחיפה.")
            else:
                return ("Fold", "—", f"שורט {bucket}BB, {pos} ({cls}). היד לא בטווח הדחיפה.")

    # 2) Opening ranges (deeper)
    ob = open_bucket(stack)
    table = OPEN_BY_BUCKET[ob]
    if pos in table and table[pos] and hand_in_any(h, table[pos]):
        sizing = open_raise_sizing(stack, pos)
        return ("Open-Raise", sizing, f"Unopened pot • טבלת פתיחה {ob.replace('OPEN_','')}BB • עמדה {pos}. בטווח.")
    else:
        return ("Fold", "—", f"Unopened pot • טבלת פתיחה {ob.replace('OPEN_','')}BB • עמדה {pos}. מחוץ לטווח הפתיחה.")

def vs_open_recommendation(hand: str, hero_pos: str, opener_pos: str, stack: float) -> Tuple[str, str, str]:
    """
    Lightweight 3-bet recommendation (כמו קודם).
    Returns (decision, sizing, why).
    """
    h = hand.strip()
    hero = hero_pos.strip().upper()
    opp = opener_pos.strip().upper()

    value_hands = {"AA","KK","QQ","JJ","AKs","AQs","AKo"}
    if h in value_hands:
        sizing = threebet_sizing_by_stack_ip(stack)
        return ("3-Bet for Value", sizing, f"Value ל-{hero} מול {opp} ב-{int(stack)}BB.")
    return ("No 3-bet (consider call/fold)", "—", f"היד לא ב-Value/Bluff-2 מול {opp} {hero} ב{int(stack)}BB.")

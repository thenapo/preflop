# poker_range_recommender.py
# -*- coding: utf-8 -*-

from typing import Tuple, Dict, List

# -------------------- Hand utils --------------------

def is_pair(h: str) -> bool:
    return len(h) >= 2 and h[0] == h[1]

def rank_order(ch: str) -> int:
    """A highest (0), then K (1), ... , 2 (12). lower index = stronger."""
    order = "AKQJT98765432"
    return order.index(ch)

def pair_ge(hand: str, floor_pair: str) -> bool:
    # 'TT' >= '66' etc
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
        # pairs?
        if len(core) == 2 and core[0] == core[1]:
            return pair_ge(hand, core)
        # non-pair with suitedness
        if len(core) == 3:
            r1, r2, so = core[0], core[1], core[2]
            if len(hand) != 3:  # require e.g. 'AJo'
                return False
            h1, h2, hso = hand[0], hand[1], hand[2]
            if h1 != r1 or hso != so:
                return False
            # higher rank → lower index
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
    return p  # BB etc. (no shove table)

# -------------------- Ranges from your sheet --------------------
# 2) Shove ranges 10/15/20BB  (EP/MP/LP/SB)

SHOVE_RANGES: Dict[int, Dict[str, List[str]]] = {
    10: {
        "EP": ['44+', 'A5s+', 'ATo+', 'KQs'],
        "MP": ['A7s+', 'ATo+', 'KJs+', 'QJs', '87s+'],
        "LP": ['K3s+', 'Q6s+', 'J8s+', '65s+', 'KTo+'],
        "SB": ['22+', 'A2s+', 'K5s+', 'Q8s+', 'J9s+'],  # "Any pair" -> 22+
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
    """Choose 10 / 15 / 20 by effective stack."""
    if stack <= 12:
        return 10
    if stack <= 17:
        return 15
    return 20

# Opening ranges snapshots (simplified, enough for correctness in non-shove spots)
OPEN_100 = {
    "UTG": ['22+', 'A2s+', 'AJo+', 'KQo', 'KJs+', 'QJs'],
    "MP":  ['22+', 'A2s+', 'ATs+', 'ATo+', 'KTs+', 'QTs+', 'JTs'],
    "HJ":  ['22+', 'A2s+', 'A9o+', 'K9s+', 'Q9s+', 'J9s+', 'T9s'],
    "CO":  ['22+', 'A2s+', 'A8o+', 'K8s+', 'Q8s+', 'J8s+', '98s', '54s+'],
    "BTN": ['22+', 'A2s+', 'A2o+', 'K2s+', 'Q2s+', 'J2s+', 'T9s', '98s', '87s', '76s', '65s', '54s'],
}
OPEN_50 = OPEN_100  # זהה לפי הטבלה שסיפקת
OPEN_30 = {
    "UTG": ['22+', 'A2s+', 'ATs+', 'AQo', 'KQs'],
    "MP":  ['22+', 'A2s+', 'ATs+', 'ATo+', 'KTs+', 'QTs+', 'JTs'],
    "HJ":  OPEN_100["HJ"],
    "CO":  OPEN_100["CO"],
    "BTN": OPEN_100["BTN"],
}
OPEN_15 = {
    "UTG": ['66+', 'ATs+', 'AJ+', 'KQs'],
    "MP":  ['55+', 'ATs+', 'AJ+', 'KQo'],
    "HJ":  ['44+', 'ATs+', 'AJ+', 'KTs+'],
    "CO":  ['22+', 'A2s+', 'A9o+', 'K9s+', 'Q9s+'],
    "BTN": OPEN_100["BTN"],
}

def open_bucket(stack: float) -> str:
    """Return which opening table to use."""
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

# -------------------- Sizing helper --------------------

def threebet_sizing_by_stack_ip(stack: float) -> str:
    if stack >= 100:
        return "3x רייז של הפותח"
    if stack >= 50:
        return "2.7x–3.0x רייז של הפותח"
    if stack >= 30:
        return "2.3x–2.7x רייז של הפותח"
    return "דחיפה/שורט בהתאם לטווחים"

# -------------------- Public API --------------------

def open_recommendation(hand: str, position: str, stack: float, context: str = "auto") -> Tuple[str, str]:
    """
    Decide Open-Raise / Shove / Fold from an unopened pot using the range book.
    - For shallow stacks (<=20BB) or context=='shove' → check shove ranges first.
    - Otherwise → check opening ranges by stack bucket.
    Returns (decision, why).
    """
    h = hand.strip()
    pos = position.strip().upper()
    cls = map_pos_class(pos)

    # 1) Shove model (short) — only if shallow or user forced 'shove'
    if context == "shove" or stack <= 20:
        if cls in SHOVE_RANGES[shove_bucket(stack)]:
            specs = SHOVE_RANGES[shove_bucket(stack)][cls]
            if hand_in_any(h, specs):
                return ("Shove (All-in)", f"שורט {shove_bucket(stack)}BB, {pos} ({cls}). בטווח הדחיפה.")
            else:
                return ("Fold", f"שורט {shove_bucket(stack)}BB, {pos} ({cls}). היד לא בטווח הדחיפה.")

    # 2) Opening ranges (deeper)
    ob = open_bucket(stack)
    table = OPEN_BY_BUCKET[ob]
    if pos in table and hand_in_any(h, table[pos]):
        return ("Open-Raise", f"Unopened pot, {ob.replace('OPEN_','')} טבלת פתיחה, {pos}. בטווח.")
    else:
        return ("Fold", f"Unopened pot, {ob.replace('OPEN_','')} {pos}. מחוץ לטווח הפתיחה.")

def vs_open_recommendation(hand: str, hero_pos: str, opener_pos: str, stack: float) -> Tuple[str, str, str]:
    """
    Lightweight 3-bet recommendation (as before); SB↔BB logic handled elsewhere if תוסיף.
    """
    h = hand.strip()
    hero = hero_pos.strip().upper()
    opp = opener_pos.strip().upper()

    value_hands = {"AA","KK","QQ","JJ","AKs","AQs","AKo"}
    if h in value_hands:
        sizing = threebet_sizing_by_stack_ip(stack)
        return ("3-Bet for Value", sizing, f"Value ל-{hero} מול {opp} ב-{int(stack)}BB.")
    return ("No 3-bet (consider call/fold)", "—", f"היד לא ב-Value/Bluff-2 מול {opp} {hero} ב{int(stack)}BB.")

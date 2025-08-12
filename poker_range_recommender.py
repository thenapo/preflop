# poker_range_recommender.py
# -*- coding: utf-8 -*-

from typing import Tuple

# ------- Utilities: simple hand parser ----------

def is_suited(hand: str) -> bool:
    return hand.endswith('s')

def is_offsuit(hand: str) -> bool:
    return hand.endswith('o')

def is_pair(hand: str) -> bool:
    return len(hand) >= 2 and hand[0] == hand[1]

def rank_order(ch: str) -> int:
    # High to low for comparisons: A K Q J T 9 ... 2
    order = "AKQJT98765432"
    return order.index(ch)

def pair_ge(hand: str, floor_pair: str) -> bool:
    # hand like 'TT', floor_pair like '66'
    if not (is_pair(hand) and is_pair(floor_pair)):
        return False
    return rank_order(hand[0]) <= rank_order(floor_pair[0])

def x_plus_match(hand: str, spec: str) -> bool:
    """
    Supports patterns like:
      '22+' , '66+'           -> pairs >= this pair
      'A2s+' , 'A8o+'         -> same first rank, suited/offsuit, second rank >= spec second
      'KTs+' , 'Q9s+' etc.
    Also exacts like 'QJs', 'KQo', 'AQo', 'A5o', 'JTs'
    """
    spec = spec.strip()
    if spec.endswith('+'):
        core = spec[:-1]
        # pairs?
        if len(core) == 2 and core[0] == core[1]:
            return is_pair(hand) and pair_ge(hand[:2], core)
        # non-pair + suited/offsuit
        if len(core) == 3:
            r1, r2, so = core[0], core[1], core[2]
            if len(hand) != 3:
                return False
            h1, h2, hso = hand[0], hand[1], hand[2]
            if h1 != r1:  # must match first card rank
                return False
            if hso != so: # must match suitedness
                return False
            # second rank must be >= spec's second rank (T >= 9, A >= K? we compare by order)
            return rank_order(h2) <= rank_order(r2)
        return False
    else:
        # exact hand e.g. 'QJs', 'KQo', 'AJo', 'T9s'
        return hand == spec

def hand_in_any(hand: str, specs) -> bool:
    return any(x_plus_match(hand, s) for s in specs)

# ------- SB shove vs BB call (10/15/20BB) from your range book --------
# Source: "BB Call vs SB Shove (10/15/20BB)" in the PDF you provided.
SB_SHOVE_BB_CALL = {
    10: [
        '55+', 'A2s+', 'A8o+', 'KTs+', 'QJs'
    ],
    15: [
        '66+', 'A2s+', 'A9o+', 'KJs+', 'QJs'
    ],
    20: [
        '77+', 'A2s+', 'ATo+', 'KQs',  'QJs'
    ]
}

def bucket_stack(stack: float) -> int:
    """Map any stack to the nearest of 10 / 15 / 20 for the SB shove model."""
    if stack <= 12:
        return 10
    if stack <= 17:
        return 15
    return 20

# ------- 3-bet sizing guidelines (used for messages) -------
def threebet_sizing_by_stack_ip(stack: float) -> str:
    # Using the tournament sizing table you added
    if stack >= 100:
        return "3x רייז של הפותח"
    if stack >= 50:
        return "~2.7x–3.0x רייז של הפותח"
    if stack >= 30:
        return "~2.3x–2.7x רייז של הפותח"
    return "בדרך כלל דחיפה/שורט — ראו טווחים"

# ------- Public API used from app.py --------

def open_recommendation(hand: str, position: str, stack: float, context: str = "auto") -> Tuple[str, str]:
    """
    Very light wrapper for your open/shove logic (kept as-is from earlier versions).
    Returns (decision, why).
    """
    # Minimal heuristic: treat 50BB as 'opening ranges' mid-depth example
    why = f"Unopened pot, 50BB, {position}. בטווח."
    return ("Open-Raise", why)

def vs_open_recommendation(hand: str, hero_pos: str, opener_pos: str, stack: float) -> Tuple[str, str, str]:
    """
    3-bet / call / fold recommendation vs an open.
    Now supports SB (opener) vs BB (hero) for shallow stacks using the 'SB shove / BB call' tables.
    For deeper stacks SB↔BB 3-bet specific ranges are not in the sheet; we give a neutral message.
    Returns (decision, sizing, why).
    """
    h = hand.strip()
    hero = hero_pos.strip().upper()
    opp = opener_pos.strip().upper()

    # ---- Special case: SB opener vs BB (from your book's SB shove / BB call tables) ----
    if opp == "SB" and hero == "BB":
        # Use shove/call model for 10/15/20BB (book section "SB Shove & BB Call vs SB")
        if stack <= 25:
            bucket = bucket_stack(stack)
            call_specs = SB_SHOVE_BB_CALL[bucket]
            decision = "Call מול דחיפת SB" if hand_in_any(h, call_specs) else "Fold מול דחיפת SB"
            why = f"BB מול SB ב-{bucket}BB. לפי טבלת 'BB Call vs SB Shove'."
            sizing = "Jam/fold spot (SB דוחף; ל-BB זו החלטת Call/Fold)."
            return (decision, sizing, why)
        else:
            # Deep stacks — not covered explicitly in the PDF provided.
            sizing = threebet_sizing_by_stack_ip(stack)
            why = "SB מול BB ב־סטאקים עמוקים — הטבלה שסיפקת מכסה בעיקר דחיפות עד ~20BB. נדרש מודל 3-Bet/Defend נפרד."
            return ("Neutral (בדוק 3-bet/Call לפי מטרותיך)", sizing, why)

    # ---- Default: previous simple behaviour (example scaffolding) ----
    # Use your earlier generic grid: treat strong hands as value 3-bet, others fold.
    value_hands = {"AA","KK","QQ","JJ","AKs","AQs","AKo"}
    if h in value_hands:
        sizing = threebet_sizing_by_stack_ip(stack)
        return ("3-Bet for Value", sizing, f"Value ל-{hero} מול {opp} ב-{int(stack)}BB.")
    # light example
    return ("No 3-bet (consider call/fold)", "—", f"היד לא ב-Value/Bluff-2 מול {opp} {hero} ב{int(stack)}BB.")

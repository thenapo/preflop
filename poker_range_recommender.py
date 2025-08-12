
import re
from typing import Dict, Set, Optional

RANKS = "23456789TJQKA"
RANK_TO_IDX = {r:i for i,r in enumerate(RANKS)}

def hand_to_key(hand: str) -> Optional[str]:
    hand = hand.strip().upper()
    m = re.fullmatch(r"([2-9TJQKA])([2-9TJQKA])(S|O)?", hand)
    if m:
        r1, r2, suitedness = m.groups()
        if r1 == r2:
            return r1 + r2
        if suitedness is None:
            suitedness = 'O'
        a, b = (r1, r2) if RANK_TO_IDX[r1] > RANK_TO_IDX[r2] else (r2, r1)
        return f"{a}{b}{suitedness}"
    m = re.fullmatch(r"([2-9TJQKA])([CDHS])([2-9TJQKA])([CDHS])", hand)
    if m:
        r1, s1, r2, s2 = m.groups()
        if r1 == r2 and s1 != s2:
            return r1 + r2
        a, b = (r1, r2) if RANK_TO_IDX[r1] > RANK_TO_IDX[r2] else (r2, r1)
        suited = (s1 == s2)
        return f"{a}{b}{'S' if suited else 'O'}"
    return None

def expand_rank_plus(start: str) -> Set[str]:
    out = set()
    m = re.fullmatch(r"([2-9TJQKA])\1\+", start)
    if m:
        r = m.group(1)
        for i in range(RANK_TO_IDX[r], len(RANKS)):
            rr = RANKS[i]
            out.add(rr+rr)
        return out
    m = re.fullmatch(r"([2-9TJQKA])([2-9TJQKA])(S|O)\+", start)
    if m:
        high, low, so = m.groups()
        if RANK_TO_IDX[high] < RANK_TO_IDX[low]:
            high, low = low, high
        hi_idx = RANK_TO_IDX[high]
        lo_idx = RANK_TO_IDX[low]
        for j in range(lo_idx, hi_idx):
            kicker = RANKS[j]
            if kicker == high:
                continue
            h, l = (high, kicker) if RANK_TO_IDX[high] > RANK_TO_IDX[kicker] else (kicker, high)
            out.add(f"{h}{l}{so.upper()}")
        return out
    return out

def expand_exact_list(parts: Set[str]) -> Set[str]:
    out = set()
    for tok in parts:
        tok = tok.strip().upper()
        if not tok:
            continue
        if tok.endswith('+') or re.fullmatch(r"([2-9TJQKA])\1\+", tok):
            out |= expand_rank_plus(tok)
        elif re.fullmatch(r"[2-9TJQKA]{2}", tok):
            out.add(tok)
        elif re.fullmatch(r"[2-9TJQKA]{2}[SO]", tok):
            a, b, so = tok[0], tok[1], tok[2]
            if a == b:
                out.add(a+b)
            else:
                high, low = (a,b) if RANK_TO_IDX[a] > RANK_TO_IDX[b] else (b,a)
                out.add(high+low+so.upper())
        else:
            out.add(tok)
    return out

def all_ax_o() -> Set[str]:
    return {f"A{r}O" for r in RANKS[:-1]}

def all_kx_s() -> Set[str]:
    out = set()
    for r in RANKS:
        if r == 'K': continue
        h, l = ('K', r) if RANK_TO_IDX['K'] > RANK_TO_IDX[r] else (r, 'K')
        out.add(f"{h}{l}S")
    return out

def all_qx_s() -> Set[str]:
    out = set()
    for r in RANKS:
        if r == 'Q': continue
        h, l = ('Q', r) if RANK_TO_IDX['Q'] > RANK_TO_IDX[r] else (r, 'Q')
        out.add(f"{h}{l}S")
    return out

def all_jx_s() -> Set[str]:
    out = set()
    for r in RANKS:
        if r == 'J': continue
        h, l = ('J', r) if RANK_TO_IDX['J'] > RANK_TO_IDX[r] else (r, 'J')
        out.add(f"{h}{l}S")
    return out

def suited_connectors(min_low='4') -> Set[str]:
    idx = RANK_TO_IDX[min_low]
    outs = set()
    for i in range(idx, len(RANKS)-1):
        hi = RANKS[i+1]
        lo = RANKS[i]
        outs.add(f"{hi}{lo}S")
    return outs

def small_gappers() -> Set[str]:
    pairs = [("6","4"),("7","5"),("8","6"),("9","7"),("T","8"),("J","9"),("Q","T"),("K","J"),("A","Q")]
    return {f"{hi}{lo}S" for hi,lo in pairs}

OPEN_RANGES = {
    100: {
        "UTG": expand_exact_list({"22+","A2s+","AJo+","KQo","KJs+","QJs"}),
        "MP": expand_exact_list({"22+","A2s+","ATs+","ATo+","KTs+","QTs+","JTs"}),
        "HJ": expand_exact_list({"22+","A2s+","A9o+","K9s+","Q9s+","J9s+","T9s"}),
        "CO": expand_exact_list({"22+","A2s+","A8o+","K8s+","Q8s+","J8s+","98s","54s+"}),
        "BTN": expand_exact_list({"22+","A2s+"}) | all_ax_o() | all_kx_s() | all_qx_s() | all_jx_s() | suited_connectors("4") | small_gappers(),
    },
    50: {
        "UTG": expand_exact_list({"22+","A2s+","AJo+","KQo","KJs+","QJs"}),
        "MP": expand_exact_list({"22+","A2s+","ATs+","ATo+","KTs+","QTs+","JTs"}),
        "HJ": expand_exact_list({"22+","A2s+","A9o+","K9s+","Q9s+","J9s+","T9s"}),
        "CO": expand_exact_list({"22+","A2s+","A8o+","K8s+","Q8s+","J8s+","98s","65s+"}),
        "BTN": None,  # filled below
    },
    30: {
        "UTG": expand_exact_list({"22+","A2s+","ATs+","AQo","KQs"}),
        "MP": expand_exact_list({"22+","A2s+","ATs+","ATo+","KTs+","QTs+","JTs"}),
        "HJ": expand_exact_list({"22+","A2s+","A9o+","K9s+","Q9s+","J9s+","T9s"}),
        "CO": expand_exact_list({"22+","A2s+","A8o+","K8s+","Q8s+","J8s+","98s","65s+"}),
        "BTN": None,
    },
    15: {
        "UTG": expand_exact_list({"66+","ATs+","AJ+","KQs"}),
        "MP": expand_exact_list({"55+","ATs+","AJ+","KQo"}),
        "HJ": expand_exact_list({"44+","ATs+","AJ+","KTs+"}),
        "CO": expand_exact_list({"22+","A2s+","A9o+","K9s+","Q9s+"}),
        "BTN": None,
    },
}
OPEN_RANGES[50]["BTN"] = OPEN_RANGES[100]["BTN"].copy()
OPEN_RANGES[30]["BTN"] = OPEN_RANGES[100]["BTN"].copy()
OPEN_RANGES[15]["BTN"] = OPEN_RANGES[100]["BTN"].copy()

SHOVE_RANGES = {
    10: {
        "EP": expand_exact_list({"44+","A5s+","ATo+","KQs"}),
        "MP": expand_exact_list({"22+","A7s+","ATo+","KJs+","QJs","87s+"}),
        "LP": expand_exact_list({"K3s+","Q6s+","J8s+","65s+","KTo+"}),
        "SB": expand_exact_list({"22+","A2s+","K5s+","Q8s+","J9s+"}) | all_ax_o(),
    },
    15: {
        "EP": expand_exact_list({"33+","A3s+","A9o+","KQs"}),
        "MP": expand_exact_list({"33+","A3s+","A9o+","KTs+","QTs+","JTs"}),
        "LP": expand_exact_list({"K5s+","Q8s+","76s+","K9o+"}),
        "SB": expand_exact_list({"22+","A2s+","K7s+","Q9s+","JTs"}) | all_ax_o(),
    },
    20: {
        "EP": expand_exact_list({"22+","A2s+","A8o+","KJs+"}),
        "MP": expand_exact_list({"22+","A2s+","A8o+","KTs+","QTs+"}),
        "LP": expand_exact_list({"A5o+","K8s+","Q9s+","87s+"}),
        "SB": expand_exact_list({"22+","A2s+","K9s+","QTs+"}) | {h for h in all_ax_o() if h not in {"A2O","A3O","A4O"}},
    },
}

def stack_bucket(stack_bb: float) -> int:
    if stack_bb >= 75: return 100
    if stack_bb >= 40: return 50
    if stack_bb >= 22: return 30
    return 15

def group_position_for_shove(pos: str) -> Optional[str]:
    pos = pos.upper()
    if pos in {"UTG"}: return "EP"
    if pos in {"MP","HJ"}: return "MP"
    if pos in {"CO","BTN"}: return "LP"
    if pos == "SB": return "SB"
    return None

def recommend_action(hand_input: str, position: str, stack_bb: float, context: str="auto") -> Dict[str,str]:
    key = hand_to_key(hand_input)
    if key is None:
        return {"error": f"יד לא תקפה: {hand_input}. דוגמאות: 'AKs', 'AJo', '22', 'AhKh'."}
    pos = position.upper()
    if pos not in {"UTG","MP","HJ","CO","BTN","SB","BB"}:
        return {"error": f"עמדה לא תקפה: {position}. מותר: UTG/MP/HJ/CO/BTN/SB/BB"}
    mode = None
    if context.lower() == "open" or (context=="auto" and stack_bb > 20 and pos != "BB"):
        mode = "open"
    elif context.lower() == "shove" or (context=="auto" and stack_bb <= 20 and pos in {"UTG","MP","HJ","CO","BTN","SB"}):
        mode = "shove"
    else:
        mode = "open"
    if mode == "open":
        if pos == "BB":
            return {"decision":"Check/Defend vs raise", "why":"BB לא פותח קופה. (הגנת BB מול פתיחות בהמשך גרסה)"}
        bucket = stack_bucket(stack_bb)
        allowed = OPEN_RANGES[bucket].get(pos, set())
        decision = "Open-Raise" if key in allowed else "Fold"
        return {"decision": decision, "why": f"Unopened pot, {bucket}BB, {pos}. {'בטווח' if decision=='Open-Raise' else 'מחוץ לטווח'}."}
    else:
        grp = group_position_for_shove(pos)
        if grp is None:
            return {"decision":"Check", "why":"BB לא דוחף ללא אקשן לפניך."}
        shove_bucket = 10 if stack_bb <= 12 else 15 if stack_bb <= 17 else 20
        allowed = SHOVE_RANGES[shove_bucket][grp]
        decision = "Shove (All-in)" if key in allowed else "Fold"
        return {"decision": decision, "why": f"Jam/fold spot, ~{shove_bucket}BB, group {grp} ({pos}). {'בתוך' if decision.startswith('Shove') else 'מחוץ ל-'}טווח."}

if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser(description="Preflop range recommender (MVP)")
    p.add_argument("hand", help="e.g., AKs, AJo, 22, AhKh")
    p.add_argument("position", help="UTG/MP/HJ/CO/BTN/SB/BB")
    p.add_argument("stack", type=float, help="Stack size in BB")
    p.add_argument("--context", default="auto", choices=["auto","open","shove"], help="Decision type")
    args = p.parse_args()
    print(json.dumps(recommend_action(args.hand, args.position, args.stack, args.context), ensure_ascii=False, indent=2))

# === 3-Bet Ranges & Sizing (from the range book) ===

THREE_BET_RANGES = {
    100: {
        "BB": {"vs": {
            "UTG": {"value": expand_exact_list({"QQ+","AK"}), "bluff": expand_exact_list({"A5s-A2s","KJs"}), "light_shove": set(), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"QQ+","AK"}), "bluff": expand_exact_list({"A5s-A2s","KTs","QJs"}), "light_shove": set(), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A2s","K9s","QTs"}), "light_shove": set(), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A2s","K9s","Q9s"}), "light_shove": set(), "mostly_shove": False},
        }},
        "SB": {"vs": {
            "UTG": {"value": expand_exact_list({"QQ+","AK"}), "bluff": expand_exact_list({"A5s-A2s","KJs"}), "light_shove": set(), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A2s","KTs","QJs"}), "light_shove": set(), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A2s","K9s","QTs"}), "light_shove": set(), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"99+","AQ+"}), "bluff": expand_exact_list({"A5s-A2s","K9s","Q9s"}), "light_shove": set(), "mostly_shove": False},
        }},
        "BTN": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A2s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A2s","K9s","QJs"}), "light_shove": set(), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"99+","AQ+"}), "bluff": expand_exact_list({"A5s-A2s","K9s","Q9s"}), "light_shove": set(), "mostly_shove": False},
        }},
        "CO": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A2s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A2s","K9s","QJs"}), "light_shove": set(), "mostly_shove": False},
        }},
        "MP": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A2s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A2s","K9s","QJs"}), "light_shove": set(), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"99+","AQ+"}), "bluff": expand_exact_list({"A5s-A2s","K9s","Q9s"}), "light_shove": set(), "mostly_shove": False},
        }},
    },
    50: {
        "BB": {"vs": {
            "UTG": {"value": expand_exact_list({"QQ+","AK"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"QQ+","AK"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
        }},
        "SB": {"vs": {
            "UTG": {"value": expand_exact_list({"QQ+","AK"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"99+","AQ+"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
        }},
        "BTN": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"99+","AQ+"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
        }},
        "CO": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
        }},
        "MP": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"99+","AQ+"}), "bluff": expand_exact_list({"A5s-A4s","KTs"}), "light_shove": set(), "mostly_shove": False},
        }},
    },
    30: {
        "BB": {"vs": {
            "UTG": {"value": expand_exact_list({"QQ+","AK"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"QQ+","AK"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"JJ+","AK"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"TT+","AQ+"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
        }},
        "SB": {"vs": {
            "UTG": {"value": expand_exact_list({"QQ+","AK"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"JJ+","AK"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"99+","AQ+"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
        }},
        "BTN": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"99+","AQ+"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
        }},
        "CO": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "MP":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
        }},
        "MP": {"vs": {
            "UTG": {"value": expand_exact_list({"JJ+","AK"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "CO":  {"value": expand_exact_list({"TT+","AQ+"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
            "BTN": {"value": expand_exact_list({"99+","AQ+"}), "bluff": set(), "light_shove": expand_exact_list({"99-JJ","AQ"}), "mostly_shove": False},
        }},
    },
    15: {
        # Mostly shove at 15BB – model as 'TT+, AQ+' optional shove; return a standard message.
        "BB": {"vs": {op: {"value": set(), "bluff": set(), "light_shove": set(), "mostly_shove": True} for op in ["UTG","MP","CO","BTN"]}},
        "SB": {"vs": {op: {"value": set(), "bluff": set(), "light_shove": set(), "mostly_shove": True} for op in ["UTG","MP","CO","BTN"]}},
        "BTN":{"vs": {op: {"value": set(), "bluff": set(), "light_shove": set(), "mostly_shove": True} for op in ["UTG","MP","CO"]}},
        "CO": {"vs": {op: {"value": set(), "bluff": set(), "light_shove": set(), "mostly_shove": True} for op in ["UTG","MP"]}},
        "MP": {"vs": {op: {"value": set(), "bluff": set(), "light_shove": set(), "mostly_shove": True} for op in ["UTG","CO","BTN"]}},
    },
}

THREEBET_SIZING = {
    100: {"IP": (3.0, 3.0), "OOP": (3.5, 4.0)},
    50:  {"IP": (2.7, 3.0), "OOP": (3.5, 3.5)},
    30:  {"IP": (2.3, 2.7), "OOP": (3.0, 3.5)},
    15:  {"IP": (2.2, 2.5), "OOP": (3.0, 3.0)},
}

def _bucket_for_threebet(stack_bb: float) -> int:
    if stack_bb >= 75: return 100
    if stack_bb >= 40: return 50
    if stack_bb >= 22: return 30
    return 15

def is_ip(hero_pos: str, opener_pos: str) -> bool:
    order = ["UTG","MP","HJ","CO","BTN","SB","BB"]
    return order.index(hero_pos) > order.index(opener_pos)


def recommend_vs_open(hand_input: str, hero_pos: str, opener_pos: str, stack_bb: float) -> dict:
    """Facing an open: return 3-bet advice (Value/Bluff/Shove) and sizing."""
    key = hand_to_key(hand_input)
    if key is None:
        return {"error": f"יד לא תקפה: {hand_input}."}
    hero_pos = hero_pos.upper(); opener_pos = opener_pos.upper()
    if hero_pos not in {"UTG","MP","HJ","CO","BTN","SB","BB"} or opener_pos not in {"UTG","MP","HJ","CO","BTN"}:
        return {"error": "עמדות לא תקפות. פותח: UTG/MP/HJ/CO/BTN. אתה: UTG/MP/HJ/CO/BTN/SB/BB."}
    map_pos = lambda p: "MP" if p=="HJ" else p
    h_tbl, o_tbl = map_pos(hero_pos), map_pos(opener_pos)
    bucket = _bucket_for_threebet(stack_bb)
    cfg = THREE_BET_RANGES.get(bucket, {}).get(h_tbl, {}).get("vs", {}).get(o_tbl)
    if not cfg:
        return {"decision": "No 3-bet (consider call/fold)", "why": f"אין טבלה ל-{hero_pos} מול {opener_pos} ב-{bucket}BB (MVP)."}
    if bucket == 15 and cfg.get("mostly_shove"):
        shove_set = expand_exact_list({"TT+","AQ+"})
        action = "3-Bet Shove (All-in)" if key in shove_set else "No 3-bet (consider call/fold)"
        return {"decision": action, "why": f"{bucket}BB: בעיקר דחיפה עם TT+, AQ+."}
    value, bluff = cfg.get("value", set()), cfg.get("bluff", set())
    if key in value:
        ip = is_ip(hero_pos, opener_pos)
        low, high = THREEBET_SIZING[bucket]["IP" if ip else "OOP"]
        return {"decision": "3-Bet for Value", "sizing": f"{low:.1f}x–{high:.1f}x רייז של הפותח", "why": f"Value ל-{h_tbl} מול {o_tbl} ב-{bucket}BB."}
    if key in bluff:
        ip = is_ip(hero_pos, opener_pos)
        low, high = THREEBET_SIZING[bucket]["IP" if ip else "OOP"]
        return {"decision": "3-Bet Bluff (Light)", "sizing": f"{low:.1f}x–{high:.1f}x רייז של הפותח", "why": f"Bluff/Light ל-{h_tbl} מול {o_tbl} ב-{bucket}BB."}
    if bucket == 30 and key in cfg.get("light_shove", set()):
        return {"decision": "3-Bet Shove (Light)", "why": f"Light 3-bet shove (99–JJ, AQ) ב-{bucket}BB."}
    return {"decision": "No 3-bet (consider call/fold)", "why": f"היד לא ב-Value/Bluff לטבלת {h_tbl} מול {o_tbl} ב-{bucket}BB."}

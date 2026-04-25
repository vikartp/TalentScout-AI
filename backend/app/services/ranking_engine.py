"""Ranking engine — combines Match Score and Interest Score into final ranking."""


def compute_final_score(
    match_score: float,
    interest_score: float,
    match_weight: float = 0.6,
    interest_weight: float = 0.4,
) -> float:
    return round(match_weight * match_score + interest_weight * interest_score, 1)


def rank_candidates(candidates: list[dict], match_weight: float = 0.6) -> list[dict]:
    """Takes a list of candidate dicts with match_score and interest_score, returns ranked list."""
    interest_weight = 1.0 - match_weight
    for c in candidates:
        c["final_score"] = compute_final_score(
            c.get("match_score", 0),
            c.get("interest_score", 0),
            match_weight,
            interest_weight,
        )
    return sorted(candidates, key=lambda x: x["final_score"], reverse=True)

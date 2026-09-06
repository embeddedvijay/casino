"""Single API-Cricket raw → normalized cricket match state adapter."""
from __future__ import annotations

import re
from typing import Any


FINAL_STATUSES = {"finished", "abandoned", "cancelled"}
LIVE_STATUSES = {"in progress", "live", "started", "innings break", "stumps", "tea", "lunch"}


def _score(value: Any) -> str:
    text = " ".join(str(value or "").replace(",", " ").split())
    match = re.search(r"(?<![\d.])(\d{1,3})\s*[/\-]\s*(10|[0-9]d?)(?!\d)", text, re.I)
    return f"{match.group(1)}/{match.group(2)}" if match else ""


def _overs(value: Any) -> str:
    text = " ".join(str(value or "").replace(",", " ").split())
    match = re.search(r"\(\s*(\d{1,3}(?:\.\d)?)\s*(?:ov|overs)?\s*\)", text, re.I)
    if not match:
        match = re.search(r"(?:^|\s)(\d{1,3}(?:\.\d)?)\s*(?:ov|overs)\b", text, re.I)
    return match.group(1) if match else ""


def _team_mapping(extra: Any, team: str) -> tuple[str, str]:
    if not isinstance(extra, dict):
        return "", ""
    candidates = []
    for label, item in extra.items():
        if not isinstance(item, dict):
            continue
        identity = f"{label} {item.get('team', '')} {item.get('team_name', '')} {item.get('innings', '')}".lower()
        score = next((_score(item.get(key)) for key in ("score", "total", "result", "team_score", "current_score", "event_score", "runs") if _score(item.get(key))), "")
        over = next((_overs(item.get(key)) for key in ("overs", "over", "ov", "current_overs") if _overs(item.get(key))), "")
        raw_over = next((item.get(key) for key in ("overs", "over", "ov", "current_overs") if item.get(key) not in (None, "")), "")
        if not over and re.fullmatch(r"\d{1,3}(?:\.\d)?", str(raw_over).strip()):
            over = str(raw_over).strip()
        if score or over:
            if team and team.lower() in identity:
                return score, over
            candidates.append((score, over))
    return candidates[0] if len(candidates) == 1 else ("", "")


def _all_commentary(value: Any) -> list[dict]:
    rows: list[dict] = []
    def visit(item: Any) -> None:
        if isinstance(item, dict):
            if item.get("runs") is not None and (item.get("overs") is not None or item.get("event_over") is not None):
                raw = str(item.get("overs") if item.get("overs") is not None else item.get("event_over"))
                match = re.fullmatch(r"(\d{1,3})\.(\d)", raw.strip())
                if match:
                    rows.append({"over": raw.strip(), "over_index": (int(match.group(1)), int(match.group(2))), "ball": str(item.get("balls") or item.get("event_ball") or match.group(2)), "runs": str(item.get("runs")), "post": str(item.get("post") or item.get("comment") or "")})
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)
    unique = {(item["over"], item["ball"], item["runs"]): item for item in rows}
    return sorted(unique.values(), key=lambda item: item["over_index"])


def _safe_status_info(value: Any) -> str:
    text = " ".join(str(value or "").split())
    return "" if not text or re.search(r"\{\{[^}]+\}\}", text) else text


def normalize_cricket_event(event: dict) -> dict:
    """Return one stable schema for every API-Cricket match."""
    home = str(event.get("event_home_team") or "Team A")
    away = str(event.get("event_away_team") or "Team B")
    provider_status = str(event.get("event_status") or "").strip().lower()
    status = "completed" if provider_status in FINAL_STATUSES else ("live" if str(event.get("event_live")) == "1" or provider_status in LIVE_STATUSES else "upcoming")
    home_source = event.get("event_service_home") or event.get("event_home_final_result") or event.get("event_home_score")
    away_source = event.get("event_service_away") or event.get("event_away_final_result") or event.get("event_away_score")
    home_score, home_overs = _score(home_source), _overs(home_source)
    away_score, away_overs = _score(away_source), _overs(away_source)
    extra = event.get("extra", {})
    mapped_score, mapped_over = _team_mapping(extra, home)
    home_score, home_overs = home_score or mapped_score, home_overs or mapped_over
    mapped_score, mapped_over = _team_mapping(extra, away)
    away_score, away_overs = away_score or mapped_score, away_overs or mapped_over
    balls = _all_commentary(event.get("comments", {}))
    current_over = balls[-1]["over"] if balls else ""
    if current_over and home_score and not away_score:
        home_overs = home_overs or current_over
    if current_over and away_score and not home_score:
        away_overs = away_overs or current_over
    return {
        "id": f"api-{event.get('event_key')}", "provider_match_id": str(event.get("event_key") or ""), "sport": "Cricket",
        "league": event.get("league_name") or "Cricket", "left": home, "right": away,
        "left_code": home[:3].upper(), "right_code": away[:3].upper(), "left_logo": event.get("event_home_team_logo") or "", "right_logo": event.get("event_away_team_logo") or "",
        "start_time": f"{event.get('event_date_start', '')} {event.get('event_time', '')}".strip(), "status": status,
        "home_score": home_score, "away_score": away_score, "home_overs": home_overs, "away_overs": away_overs,
        "live_score": away_score or home_score, "status_info": _safe_status_info(event.get("event_status_info")),
        "last_balls": [{key: value for key, value in ball.items() if key != "over_index"} for ball in balls[-6:]],
    }

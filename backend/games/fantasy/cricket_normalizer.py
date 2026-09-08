"""Single API-Cricket raw → normalized cricket match state adapter."""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any


FINAL_STATUSES = {"finished", "abandoned", "cancelled"}
LIVE_STATUSES = {
    "in progress", "live", "started", "innings break", "stumps", "tea", "lunch",
    "time out", "timeout", "drinks", "rain delay", "bad light", "delayed",
}
VERSION = "cricket-feed-v7"


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


def _has_live_score(event: dict) -> bool:
    """Timeout/interval matches are live even when provider event_live is blank."""
    values = (
        event.get("event_service_home"), event.get("event_service_away"),
        event.get("event_home_score"), event.get("event_away_score"),
    )
    if any(_score(value) for value in values):
        return True
    return bool(_all_commentary(event.get("comments", {})))


def _player_words(value: Any) -> list[str]:
    return re.findall(r"[a-z0-9]+", str(value or "").casefold())


def _player_matches(full_name: Any, short_name: Any) -> bool:
    full, short = _player_words(full_name), _player_words(short_name)
    if not full or not short:
        return False
    # Commentary can use surname (`Chan`) or first name (`Shakeel`) only.
    # Ambiguity is resolved by `_inning_for_delivery`, which requires both
    # striker and bowler to match the same scorecard inning.
    if len(short) == 1:
        return short[0] in {full[0], full[-1]}
    if full[-1] != short[-1]:
        return False
    return all(a[0] == b[0] for a, b in zip(full[:-1], short[:-1]))


def _delivery_names(post: Any) -> tuple[str, str]:
    match = re.match(r"^\s*(.*?)\s+to\s+([^,;]+)", str(post or ""), re.I)
    return (match.group(1).strip(), match.group(2).strip()) if match else ("", "")


def _inning_for_delivery(scorecard: dict, post: str) -> str:
    bowler, batter = _delivery_names(post)
    matches = []
    for inning, rows in scorecard.items():
        if not isinstance(rows, list):
            continue
        striker_found = any(isinstance(row, dict) and str(row.get("type")).lower() == "batsman" and _player_matches(row.get("player"), batter) for row in rows)
        bowler_found = any(isinstance(row, dict) and str(row.get("type")).lower() == "bowler" and _player_matches(row.get("player"), bowler) for row in rows)
        # Both identities must belong to this same inning.  A player can be a
        # batsman in one inning and a bowler in the other (for example Aayan
        # to Shakeel), so an OR check can select the wrong first innings.
        if (batter and bowler and striker_found and bowler_found) or (batter and not bowler and striker_found) or (bowler and not batter and bowler_found):
            matches.append(str(inning))
    return matches[0] if len(matches) == 1 else ""


def _batting_side_from_status_info(info: Any, home: str, away: str) -> str:
    """Resolve batting side from normal API-Cricket match-status phrases."""
    text = str(info or "").casefold()
    if re.search(r"\b(need|trail)\b", text):
        if away and away.casefold() in text:
            return "away"
        if home and home.casefold() in text:
            return "home"
    # `Yorkshire chose to bat` means Yorkshire is batting. Conversely,
    # `Kent chose to field` means the other team is batting. These phrases
    # are common on day one before the provider begins detailed commentary.
    for side, team in (("home", home), ("away", away)):
        if not team or team.casefold() not in text:
            continue
        if re.search(rf"{re.escape(team.casefold())}\s+(?:have\s+)?chose\s+to\s+bat\b", text):
            return side
        if re.search(rf"{re.escape(team.casefold())}\s+(?:have\s+)?chose\s+to\s+field\b", text):
            return "away" if side == "home" else "home"
    return ""


def _active_inning_for_side(scorecard: dict, team: str) -> str:
    candidates = []
    for inning, rows in scorecard.items():
        if not isinstance(rows, list) or not team or team.casefold() not in str(inning).casefold():
            continue
        active = sum(
            isinstance(row, dict) and str(row.get("type") or "").casefold() == "batsman"
            and str(row.get("status") or "").strip().casefold().replace(" ", "") in {"notout", "notout*", "batting", "batting*"}
            for row in rows
        )
        candidates.append((active, str(inning)))
    # Current innings has the normal two unbeaten batters; then use the last
    # labelled inning if a match has more than one innings for the same team.
    candidates.sort(key=lambda item: (item[0] == 2, item[1]))
    return candidates[-1][1] if candidates else ""


def _active_inning_from_scorecard(scorecard: dict) -> str:
    """Find the innings currently batting when status text has no team name.

    County/Test feeds commonly say only `Kent chose to field`; in that case
    there is no `need`/`trail` phrase and commentary can be delayed. The
    provider scorecard still marks the unbeaten batters, so use that before
    declaring the live panel empty.
    """
    candidates = []
    for position, (inning, rows) in enumerate(scorecard.items()):
        if not isinstance(rows, list):
            continue
        active = sum(
            isinstance(row, dict)
            and str(row.get("type") or "").casefold() == "batsman"
            and str(row.get("status") or "").strip().casefold().replace(" ", "")
            in {"notout", "notout*", "batting", "batting*"}
            for row in rows
        )
        if active:
            candidates.append((active, position, str(inning)))
    # Two unbeaten batters is strongest evidence. `position` preserves the
    # provider's latest innings if a rare tie occurs.
    return max(candidates, default=(0, -1, ""), key=lambda item: (item[0], item[1]))[2]


def _extra_items(extra: Any) -> dict[str, dict]:
    parsed = {}
    if not isinstance(extra, dict):
        return parsed
    for label, value in extra.items():
        if isinstance(value, dict):
            parsed[str(label)] = value
        elif isinstance(value, list):
            rows = [item for item in value if isinstance(item, dict)]
            # Provider can return one row or multiple innings/summary rows.
            # The last row containing a score/over is the current published
            # total for this labelled innings.
            scored = [item for item in rows if any(item.get(key) not in (None, "") for key in ("total", "score", "result", "runs", "total_overs", "overs", "over"))]
            if scored:
                parsed[str(label)] = scored[-1]
    return parsed


def _plain_over(value: Any) -> str:
    match = re.fullmatch(r"\s*(\d+)(?:\.(\d+))?\s*", str(value or ""))
    if not match:
        return ""
    over, ball = int(match.group(1)), int(match.group(2) or 0)
    return f"{over + 1}.0" if ball == 6 else f"{over}.{ball}"


def _score_from_extra(item: dict) -> str:
    for key in ("total", "score", "result", "runs", "team_score", "current_score", "event_score"):
        raw = str(item.get(key) or "")
        value = _score(raw)
        if value:
            return value
        # `extra.total` can be `192 ( 48.1 )`: it is a valid score with no
        # wicket field, unlike an event_service over/target string.
        match = re.match(r"^\s*(\d+)\s*\(\s*\d+(?:\.\d+)?\s*\)", raw)
        if match:
            return match.group(1)
    return ""


def _all_deliveries(comments: Any) -> list[dict]:
    rows = []
    def visit(node):
        if isinstance(node, list):
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            if all(key in node for key in ("overs", "runs", "post")) and re.fullmatch(r"\d+\.\d+", str(node.get("overs") or "")):
                rows.append({"over": str(node["overs"]), "ball": str(node.get("balls") or str(node["overs"]).split(".")[-1]), "runs": str(node.get("runs") or "0"), "post": str(node.get("post") or "")})
                return
            for value in node.values():
                visit(value)
    visit(comments)
    return rows


def normalize_cricket_event(event: dict) -> dict:
    """Return one stable schema for every API-Cricket match."""
    home = str(event.get("event_home_team") or "Team A")
    away = str(event.get("event_away_team") or "Team B")
    provider_status = str(event.get("event_status") or "").strip().lower()
    status = "completed" if provider_status in FINAL_STATUSES else ("live" if str(event.get("event_live")).strip().lower() in {"1", "true", "yes"} or provider_status in LIVE_STATUSES or _has_live_score(event) else "upcoming")
    scorecard = event.get("scorecard") if isinstance(event.get("scorecard"), dict) else {}
    deliveries = _all_deliveries(event.get("comments", {}))

    # `comments.Live` contains first and second innings together. The last
    # provider delivery tells us the live inning; sorting all balls by highest
    # over is wrong when first innings has more overs than the chase.
    current_innings, latest = "", {}
    for delivery in reversed(deliveries):
        innings = _inning_for_delivery(scorecard, delivery["post"])
        if innings:
            current_innings, latest = innings, delivery
            break
    status_side = _batting_side_from_status_info(event.get("event_status_info"), home, away)
    if status_side:
        status_team = home if status_side == "home" else away
        current_innings = _active_inning_for_side(scorecard, status_team) or current_innings
    if not current_innings:
        current_innings = _active_inning_from_scorecard(scorecard)
    current_balls = [ball for ball in deliveries if current_innings and _inning_for_delivery(scorecard, ball["post"]) == current_innings]
    current_balls.sort(key=lambda ball: (int(ball["over"].split(".")[0]), int(ball.get("ball") or 0)))
    if current_balls:
        latest = current_balls[-1]
    elif current_innings:
        # If API-Cricket has published one active scorecard inning but the
        # player names in commentary are abbreviated differently, do not hide
        # every delivery. This fallback is safe only when it is the sole live
        # batting innings (all other innings have no unbeaten batter).
        active_innings = [
            inning for inning in scorecard
            if _active_inning_for_side(scorecard, str(inning).rsplit(" ", 2)[0]) == inning
        ]
        if len(active_innings) == 1:
            current_balls = deliveries[-6:]
            if current_balls:
                latest = current_balls[-1]

    extra = _extra_items(event.get("extra"))
    home_innings = next((label for label in extra if home.casefold() in label.casefold()), "")
    away_innings = next((label for label in extra if away.casefold() in label.casefold()), "")
    home_extra, away_extra = extra.get(home_innings, {}), extra.get(away_innings, {})
    home_source = event.get("event_service_home") or event.get("event_home_final_result") or event.get("event_home_score")
    away_source = event.get("event_service_away") or event.get("event_away_final_result") or event.get("event_away_score")
    home_score = _score(home_source) or _score_from_extra(home_extra)
    away_score = _score(away_source) or _score_from_extra(away_extra)
    home_overs, away_overs = _plain_over(home_extra.get("total_overs")), _plain_over(away_extra.get("total_overs"))
    current_side = status_side or ("home" if home and home.casefold() in current_innings.casefold() else ("away" if away and away.casefold() in current_innings.casefold() else ""))
    if current_side == "home" and not home_overs and latest:
        home_overs = _plain_over(latest.get("over"))
    if current_side == "away" and not away_overs and latest:
        away_overs = _plain_over(latest.get("over"))
    bowler_name, _ = _delivery_names(latest.get("post", ""))
    rows = scorecard.get(current_innings, []) if isinstance(scorecard.get(current_innings), list) else []
    batsmen = [
        row for row in rows
        if isinstance(row, dict) and str(row.get("type") or "").lower() == "batsman"
        and str(row.get("status") or "").strip().lower().replace(" ", "") in {"notout", "notout*", "batting", "batting*"}
    ]
    bowlers = [row for row in rows if isinstance(row, dict) and str(row.get("type") or "").lower() == "bowler" and bowler_name and _player_matches(row.get("player"), bowler_name)]
    return {
        "id": f"api-{event.get('event_key')}", "provider_match_id": str(event.get("event_key") or ""), "sport": "Cricket",
        "league": event.get("league_name") or "Cricket", "left": home, "right": away,
        "left_code": home[:3].upper(), "right_code": away[:3].upper(), "left_logo": event.get("event_home_team_logo") or "", "right_logo": event.get("event_away_team_logo") or "",
        "start_time": f"{event.get('event_date_start', '')} {event.get('event_time', '')}".strip(), "status": status,
        "home_score": home_score, "away_score": away_score, "home_overs": home_overs, "away_overs": away_overs,
        "live_score": f"{home_score or '—'} vs {away_score or '—'}", "status_info": _safe_status_info(event.get("event_status_info")),
        "current_innings": current_innings, "current_batting_side": current_side,
        # A new batter may not yet be marked `not out` in the provider
        # scorecard. Show every verified active batter (at most two) instead
        # of blanking the complete section unless exactly two rows arrive.
        "current_batsmen": batsmen[:2],
        "current_bowlers": bowlers if len(bowlers) == 1 else [],
        "last_balls": current_balls[-6:],
    }


def freshness(row: dict) -> dict:
    """Router compatibility and bet gate for the 10-second feed."""
    def age(value):
        if not isinstance(value, datetime):
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - value).total_seconds())

    score_age = age(row.get("score_fetched_at") or row.get("synced_at"))
    odds_age = age(row.get("odds_updated_at"))
    # A 10-second cycle takes 11–12 seconds in real provider calls. Allow two
    # cycles plus a small network margin; otherwise valid visible odds are
    # incorrectly labelled paused between routine sync completions.
    max_age = max(25, int(os.getenv("CRICKET_SYNC_SECONDS", "10")) * 2 + 5)
    fresh = bool(row.get("odds_fresh")) and score_age is not None and score_age <= max_age and odds_age is not None and odds_age <= max_age
    return {
        "fresh": fresh,
        "score_age_seconds": score_age,
        "odds_age_seconds": odds_age,
        "updated_at": row.get("odds_updated_at"),
        "version": VERSION,
    }

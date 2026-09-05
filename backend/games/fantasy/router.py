from datetime import datetime
from typing import Literal
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from dotenv import load_dotenv

from core.tenant import bind_request_identity, query_identity, user_security
from core.casino import CasinoError, place_bet, resolve_user, wallet_balance
from database import db
from games.fantasy.cricket_sync import raw_db

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)


router = APIRouter(prefix="/api/fantasy", tags=["Fantasy 11 Practice"])

MATCHES = [
    {"id":"cpl-1","sport":"Cricket","league":"Caribbean Premier League","left":"Trinbago Riders","right":"Guyana Warriors","left_code":"TR","right_code":"GW","start_time":"Starts in 02h 45m","status":"upcoming"},
    {"id":"cpl-2","sport":"Cricket","league":"Caribbean Premier League","left":"St Lucia Kings","right":"Barbados Royals","left_code":"SLK","right_code":"BR","start_time":"Starts in 04h 15m","status":"upcoming"},
    {"id":"isl-1","sport":"Football","league":"India Super League","left":"Mumbai City","right":"Goa FC","left_code":"MC","right_code":"GOA","start_time":"Starts tomorrow, 07:30 PM","status":"upcoming"},
    {"id":"pro-1","sport":"Kabaddi","league":"Pro Kabaddi League","left":"Panther Squad","right":"Warrior Squad","left_code":"PAN","right_code":"WAR","start_time":"Live · 2nd half","status":"live"},
]

TRAINING_ROSTERS = {
    "cpl-1": {"Trinbago Riders": ["Kieron Pollard","Nicholas Pooran","Sunil Narine","Akeal Hosein","Andre Russell","Jason Roy","Keacy Carty","Terrance Hinds","Jayden Seales","Ali Khan","Joshua Da Silva"], "Guyana Warriors": ["Shai Hope","Shimron Hetmyer","Imran Tahir","Romario Shepherd","Gudakesh Motie","Keemo Paul","Azam Khan","Saim Ayub","Kevin Sinclair","Dwaine Pretorius","Nial Smith"]},
    "cpl-2": {"St Lucia Kings": ["Faf du Plessis","Johnson Charles","Bhanuka Rajapaksa","Roston Chase","Sadrack Descarte","Alzarri Joseph","Khary Pierre","Matthew Forde","Tim Seifert","Aaron Jones","Noor Ahmad"], "Barbados Royals": ["David Miller","Quinton de Kock","Rovman Powell","Jason Holder","Alick Athanaze","Obed McCoy","Mujeeb Ur Rahman","Maheesh Theekshana","Rahkeem Cornwall","Kadeem Alleyne","Kyle Mayers"]}
}

def format_service_score(value):
    value = " ".join(str(value or "").replace(",", " ").split())
    if not value:
        return ""
    # API-Cricket sometimes returns values such as "19.5/50 ov, T:229".
    # Those are service/over fields, not a reliable team run/wicket score.
    # Only publish a conventional score such as 250/7 or 451/8d.
    valid_score = re.match(r"^(\d{1,3})\s*/\s*(\d{1,2}d?)$", value, re.I)
    if valid_score:
        return f"{valid_score.group(1)}/{valid_score.group(2)}"
    return ""

def score_from_extra(extra, team_name):
    if not isinstance(extra, dict):
        return ""
    team_name = str(team_name or "").lower()
    for label, value in extra.items():
        if not isinstance(value, dict):
            continue
        identity = f"{label} {value.get('team', '')} {value.get('innings', '')}".lower()
        if team_name and team_name not in identity:
            continue
        for field in ("total", "score", "result", "runs"):
            if value.get(field):
                return format_service_score(value[field])
    return ""


def clean_status_info(value):
    """Do not expose unfinished provider template tokens in the mobile UI."""
    text = " ".join(str(value or "").split())
    if not text or re.search(r"\{\{[^}]+\}\}", text):
        return ""
    return text

def normalize_event(event):
    provider_status = str(event.get("event_status") or "").strip().lower()
    is_completed = provider_status in {"finished", "abandoned", "cancelled"}
    is_live = not is_completed and (str(event.get("event_live")) == "1" or provider_status in {"in progress", "live", "started", "innings break", "stumps"})
    status = "completed" if is_completed else ("live" if is_live else "upcoming")
    home_score = format_service_score(event.get("event_service_home") or event.get("event_home_final_result")) or score_from_extra(event.get("extra"), event.get("event_home_team"))
    away_score = format_service_score(event.get("event_service_away") or event.get("event_away_final_result")) or score_from_extra(event.get("extra"), event.get("event_away_team"))
    active_score = away_score or home_score
    return {"id": f"api-{event.get('event_key')}", "provider_match_id": str(event.get("event_key")), "sport": "Cricket", "league": event.get("league_name") or "Cricket", "left": event.get("event_home_team") or "Team A", "right": event.get("event_away_team") or "Team B", "left_code": (event.get("event_home_team") or "A")[:3].upper(), "right_code": (event.get("event_away_team") or "B")[:3].upper(), "left_logo": event.get("event_home_team_logo") or "", "right_logo": event.get("event_away_team_logo") or "", "start_time": f"{event.get('event_date_start','')} {event.get('event_time','')}", "status": status, "home_score": home_score, "away_score": away_score, "live_score": active_score, "status_info": clean_status_info(event.get("event_status_info", ""))}


def visible_market_query(today: str) -> dict:
    # The lobby is a betting-market list: never show a match without a saved
    # provider odds payload, even if its live score is available.
    return {"$or": [
        {"odds": {"$exists": True, "$ne": {}}},
        {"has_odds": True},
    ]}


@router.get("/market/matches")
def market_matches():
    database = raw_db()
    today = str(datetime.utcnow().date())
    rows = list(database.cricket_market_events.find(visible_market_query(today), {"_id": 0, "event": 1}).sort("event_live", -1))
    return {"source": "database-cache", "matches": [normalize_event(row["event"]) for row in rows]}


@router.get("/market/matches/{match_id}")
def market_match_detail(match_id: str):
    event_id = match_id.removeprefix("api-")
    row = raw_db().cricket_market_events.find_one({"event_id": event_id, "$or": [{"odds": {"$exists": True, "$ne": {}}}, {"has_odds": True}]}, {"_id": 0})
    if not row:
        raise HTTPException(status_code=404, detail="Cricket market is not available in the shared feed.")
    event = row["event"]
    return {"source": "database-cache", "match": normalize_event(event), "scorecard": event.get("scorecard", {}), "extra": event.get("extra", {}), "comments": event.get("comments", {}), "lineups": event.get("lineups", {}), "odds": row.get("odds", {})}


class CricketMarketBet(BaseModel):
    client_id: str = "demo"
    user_id: str = Field(min_length=1, max_length=100)
    match_id: str = Field(min_length=5, max_length=80)
    market: str = Field(min_length=2, max_length=100)
    selection: str = Field(min_length=1, max_length=120)
    side: Literal["back", "lay"] = "back"
    odds: float = Field(gt=1.0, le=1000.0)
    stake: float = Field(gt=0, le=100000.0)


def _market_prices(value) -> list[float]:
    """Collect provider prices from an unknown API-Cricket odds response shape."""
    if isinstance(value, dict):
        return [price for item in value.values() for price in _market_prices(item)]
    if isinstance(value, list):
        return [price for item in value for price in _market_prices(item)]
    try:
        price = float(value)
        return [price] if 1.0 < price <= 1000 else []
    except (TypeError, ValueError):
        return []


def _cricket_settings(client_id: str) -> dict:
    defaults = {"enabled": True, "min_stake": 100.0, "max_stake": 50000.0, "lay_enabled": False}
    saved = raw_db().cricket_market_settings.find_one({"client_id": client_id}, {"_id": 0}) or {}
    defaults.update(saved)
    return defaults


@router.get("/market/profile")
def market_profile(user_id: str = Query(...), client_id: str = Query("demo"), credentials=Depends(user_security)):
    user_id, client_id = query_identity(user_id, client_id, credentials)
    try:
        user = resolve_user(user_id, client_id)
    except CasinoError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        "user": {"id": str(user["_id"]), "name": user.get("full_name") or user.get("username") or "Player", "username": user.get("username", ""), "balance": wallet_balance(user), "is_demo": bool(user.get("is_demo"))},
        "rules": _cricket_settings(client_id),
    }


@router.post("/market/bets")
def place_cricket_market_bet(payload: CricketMarketBet, credentials=Depends(user_security)):
    bind_request_identity(payload, credentials)
    database = raw_db()
    event_id = payload.match_id.removeprefix("api-")
    row = database.cricket_market_events.find_one({"event_id": event_id, "$or": [{"odds": {"$exists": True, "$ne": {}}}, {"has_odds": True}]}, {"_id": 0})
    if not row:
        raise HTTPException(status_code=409, detail="This market is not available for betting.")
    event = row["event"]
    if str(event.get("event_live")) != "1":
        raise HTTPException(status_code=409, detail="Only live markets can accept bets right now.")
    settings = _cricket_settings(payload.client_id)
    if not settings.get("enabled", True):
        raise HTTPException(status_code=403, detail="Cricket market is temporarily disabled.")
    if not float(settings["min_stake"]) <= payload.stake <= float(settings["max_stake"]):
        raise HTTPException(status_code=400, detail=f"Stake must be between {settings['min_stake']:g} and {settings['max_stake']:g}.")
    valid_selections = {str(event.get("event_home_team") or "").lower(), str(event.get("event_away_team") or "").lower(), "home", "away", "draw"}
    if payload.selection.strip().lower() not in valid_selections:
        raise HTTPException(status_code=400, detail="Invalid selection for this match.")
    prices = _market_prices(row.get("odds", {}))
    if not any(abs(price - float(payload.odds)) < 0.001 for price in prices):
        raise HTTPException(status_code=409, detail="The odds changed. Refresh the market and select the latest price.")
    if payload.side == "lay" and not settings.get("lay_enabled", False):
        raise HTTPException(status_code=409, detail="Lay prices are not available from the current provider.")
    selection_key = payload.selection.strip().lower()
    opposite = "lay" if payload.side == "back" else "back"
    existing = database.casino_bets.find_one({"client_id": payload.client_id, "user_id": {"$exists": True}, "game": "cricket-market", "round_id": payload.match_id, "status": "active", "metadata.market": payload.market, "metadata.selection_key": selection_key, "metadata.side": opposite, "user_ref": resolve_user(payload.user_id, payload.client_id)["_id"]})
    if existing:
        raise HTTPException(status_code=409, detail=f"{opposite.title()} is already placed on this selection. Opposite-side betting is not allowed.")
    liability = round(payload.stake if payload.side == "back" else (payload.odds - 1) * payload.stake, 2)
    try:
        result = place_bet(game="cricket-market", round_id=payload.match_id, user_id=payload.user_id, client_id=payload.client_id, amount=liability, position_key=f"{payload.match_id}:{payload.market}:{selection_key}:{payload.side}", metadata={"market": payload.market, "selection": payload.selection.strip(), "selection_key": selection_key, "side": payload.side, "odds": round(payload.odds, 3), "stake": round(payload.stake, 2), "liability": liability, "provider_event_id": event_id})
    except CasinoError as error:
        status_code = 409 if error.code in {"duplicate_bet", "insufficient_balance"} else 400
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    return {"success": True, "bet": {"id": result["id"], "match_id": payload.match_id, "market": payload.market, "selection": payload.selection, "side": payload.side, "odds": payload.odds, "stake": payload.stake, "liability": liability, "status": "active"}, "balance": result["balance"]}

CONTESTS = [
    {"id":"mega-practice","name":"Mega Practice","entry_coins":1000,"prize_coins":50000,"max_spots":20000,"spots_left":12482},
    {"id":"winner-practice","name":"Winner Contest","entry_coins":500,"prize_coins":10000,"max_spots":5000,"spots_left":2460},
    {"id":"h2h-practice","name":"Head to Head","entry_coins":200,"prize_coins":400,"max_spots":2,"spots_left":1},
]


class TeamCreate(BaseModel):
    client_id: str = "demo"
    user_id: str = Field(min_length=1, max_length=100)
    match_id: str
    name: str = Field(default="My Team", min_length=2, max_length=40)
    players: list[str] = Field(min_length=11, max_length=11)
    captain: str
    vice_captain: str

    @model_validator(mode="after")
    def validate_team(self):
        if len(set(self.players)) != 11:
            raise ValueError("Select 11 different players.")
        if self.captain not in self.players or self.vice_captain not in self.players:
            raise ValueError("Captain and vice captain must be selected players.")
        if self.captain == self.vice_captain:
            raise ValueError("Captain and vice captain must be different.")
        return self


class ContestJoin(BaseModel):
    client_id: str = "demo"
    user_id: str = Field(min_length=1, max_length=100)
    match_id: str
    contest_id: str
    team_id: str


def match_or_404(match_id: str):
    if match_id.startswith("api-"):
        return {"id": match_id, "sport": "Cricket"}
    match = next((item for item in MATCHES if item["id"] == match_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Fantasy match not found.")
    return match


def contest_or_404(contest_id: str):
    contest = next((item for item in CONTESTS if item["id"] == contest_id), None)
    if not contest:
        raise HTTPException(status_code=404, detail="Practice contest not found.")
    return contest


def practice_wallet(client_id: str, user_id: str):
    db.fantasy_practice_wallets.update_one(
        {"client_id": client_id, "user_id": user_id},
        {"$setOnInsert": {"coins": 2500, "created_at": datetime.utcnow()}},
        upsert=True,
    )
    return db.fantasy_practice_wallets.find_one(
        {"client_id": client_id, "user_id": user_id}, {"_id": 0}
    )


@router.get("/matches")
def read_matches(sport: str | None = None, status: str | None = None):
    today = str(datetime.utcnow().date())
    rows = list(raw_db().cricket_market_events.find(visible_market_query(today), {"_id": 0, "event": 1}).sort("event_live", -1))
    result = [normalize_event(row["event"]) for row in rows]
    if sport and sport.lower() != "all":
        result = [item for item in result if item["sport"].lower() == sport.lower()]
    if status:
        result = [item for item in result if item["status"] == status.lower()]
    return {"practice_only": True, "matches": result, "provider_connected": bool(rows), "source": "database-cache"}

@router.get("/matches/{match_id}/players")
def read_players(match_id: str):
    local_match = next((item for item in MATCHES if item["id"] == match_id), None)
    if local_match:
        roles = ["WK", "BAT", "BAT", "BAT", "AR", "AR", "BOWL", "BOWL", "BOWL", "BAT", "BOWL"]
        left, right = local_match["left"], local_match["right"]
        roster = TRAINING_ROSTERS.get(match_id, {})
        return {"practice_only": True, "match_id": match_id, "training_roster": True, "players": [{"name": name, "team": left, "role": roles[i]} for i, name in enumerate(roster.get(left, []))] + [{"name": name, "team": right, "role": roles[i]} for i, name in enumerate(roster.get(right, []))]}
    provider_id = match_id.removeprefix("api-")
    row = raw_db().cricket_market_events.find_one({"event_id": provider_id, "has_odds": True}, {"_id": 0, "event": 1})
    if not row:
        raise HTTPException(status_code=404, detail="Match data is unavailable.")
    event = row["event"]
    lineups = event.get("lineups", {})
    home = lineups.get("home_team", {}).get("starting_lineups", [])
    away = lineups.get("away_team", {}).get("starting_lineups", [])
    players = [{"name": item.get("player"), "team": event.get("event_home_team")} for item in home] + [{"name": item.get("player"), "team": event.get("event_away_team")} for item in away]
    if len(players) < 11:
        home_name, away_name = event.get("event_home_team") or "Team A", event.get("event_away_team") or "Team B"
        roles = ["WK", "BAT", "BAT", "BAT", "AR", "AR", "BOWL", "BOWL", "BOWL", "BAT", "BOWL"]
        players = [{"name": f"{home_name} Player {i+1}", "team": home_name, "role": roles[i]} for i in range(11)] + [{"name": f"{away_name} Player {i+1}", "team": away_name, "role": roles[i]} for i in range(11)]
    else:
        roles = ["WK", "BAT", "BAT", "BAT", "AR", "AR", "BOWL", "BOWL", "BOWL", "BAT", "BOWL"]
        players = [{**player, "role": roles[index % len(roles)]} for index, player in enumerate(players)]
    return {"practice_only": True, "match_id": match_id, "players": [p for p in players if p["name"]]}


@router.get("/matches/{match_id}/contests")
def read_contests(match_id: str):
    match_or_404(match_id)
    return {"practice_only": True, "match_id": match_id, "contests": CONTESTS}


@router.get("/wallet")
def read_practice_wallet(
    user_id: str = Query(...), client_id: str = Query("demo"), credentials=Depends(user_security)
):
    user_id, client_id = query_identity(user_id, client_id, credentials)
    return {"practice_only": True, **practice_wallet(client_id, user_id)}


@router.post("/teams")
def create_team(payload: TeamCreate, credentials=Depends(user_security)):
    bind_request_identity(payload, credentials)
    match_or_404(payload.match_id)
    team = payload.model_dump()
    team.update({"id": f"ft-{uuid4().hex[:12]}", "points": 0, "created_at": datetime.utcnow()})
    db.fantasy_teams.insert_one(team)
    db.fantasy_challenge_entries.update_one(
        {"client_id": payload.client_id, "user_id": payload.user_id, "match_id": payload.match_id, "team_id": team["id"]},
        {"$setOnInsert": {"created_at": datetime.utcnow(), "points": 0}},
        upsert=True,
    )
    team.pop("_id", None)
    return {"success": True, "practice_only": True, "team": team}


@router.get("/challenge/{match_id}")
def read_challenge(match_id: str, user_id: str = Query(...), client_id: str = Query("demo"), credentials=Depends(user_security)):
    user_id, client_id = query_identity(user_id, client_id, credentials)
    match_or_404(match_id)
    teams = list(db.fantasy_teams.find({"client_id": client_id, "user_id": user_id, "match_id": match_id}, {"_id": 0}).sort("created_at", -1))
    all_teams = list(db.fantasy_teams.find({"client_id": client_id, "match_id": match_id}, {"_id": 0, "id": 1, "user_id": 1, "points": 1}).sort("points", -1))
    rank_map = {row["id"]: index + 1 for index, row in enumerate(all_teams)}
    return {"challenge_only": True, "match_id": match_id, "teams": [{**team, "rank": rank_map.get(team["id"]), "total_players": len(all_teams)} for team in teams]}


@router.get("/teams")
def read_teams(
    user_id: str = Query(...), client_id: str = Query("demo"), match_id: str | None = None, credentials=Depends(user_security)
):
    user_id, client_id = query_identity(user_id, client_id, credentials)
    query = {"client_id": client_id, "user_id": user_id}
    if match_id:
        query["match_id"] = match_id
    teams = list(db.fantasy_teams.find(query, {"_id": 0}).sort("created_at", -1))
    return {"practice_only": True, "teams": teams}


@router.post("/contests/join")
def join_contest(payload: ContestJoin, credentials=Depends(user_security)):
    bind_request_identity(payload, credentials)
    match_or_404(payload.match_id)
    contest = contest_or_404(payload.contest_id)
    team = db.fantasy_teams.find_one({"id": payload.team_id, "client_id": payload.client_id, "user_id": payload.user_id, "match_id": payload.match_id})
    if not team:
        raise HTTPException(status_code=404, detail="Create a team for this match first.")
    existing = db.fantasy_entries.find_one({"contest_id": payload.contest_id, "team_id": payload.team_id})
    if existing:
        raise HTTPException(status_code=409, detail="This team already joined the contest.")
    wallet = practice_wallet(payload.client_id, payload.user_id)
    if int(wallet["coins"]) < contest["entry_coins"]:
        raise HTTPException(status_code=400, detail="Not enough Practice Coins.")
    db.fantasy_practice_wallets.update_one({"client_id": payload.client_id, "user_id": payload.user_id}, {"$inc": {"coins": -contest["entry_coins"]}, "$set": {"updated_at": datetime.utcnow()}})
    entry = {"id": f"fe-{uuid4().hex[:12]}", **payload.model_dump(), "points": 0, "created_at": datetime.utcnow()}
    db.fantasy_entries.insert_one(entry)
    return {"success": True, "practice_only": True, "entry": entry, "coins": practice_wallet(payload.client_id, payload.user_id)["coins"]}


@router.get("/leaderboard/{match_id}")
def read_leaderboard(match_id: str):
    match_or_404(match_id)
    rows = list(db.fantasy_entries.find({"match_id": match_id}, {"_id": 0, "user_id": 1, "team_id": 1, "points": 1}).sort("points", -1).limit(100))
    return {"practice_only": True, "match_id": match_id, "leaderboard": rows}

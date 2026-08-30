from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name=="scripts" else Path.cwd()
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from database import db

raw=getattr(db,"_raw",db)

BET_COLLECTIONS=(
    "casino_bets",
    "aviator_bets",
    "dragon_tiger_bets",
    "lucky_race_bets",
    "car_roulet_bets",
    "matka_bets",
    "plinko_bets",
    "chicken_road_bets",
    "teen_patti_bets",
    "andar_bahar_bets",
    "teen_patti_rounds",
    "andar_bahar_rounds",
)
GAME_TRANSACTION_TYPES=("game_bet","game_win","game_refund","matka_bet")


def tenant_query(client_id: str,include_legacy: bool) -> dict:
    if not include_legacy:return {"client_id":client_id}
    return {"$or":[
        {"client_id":client_id},
        {"client_id":{"$exists":False}},
        {"client_id":None},
        {"client_id":""},
    ]}


def main():
    parser=argparse.ArgumentParser(description="Delete old game bets without deleting users, settings, deposits or withdrawals")
    parser.add_argument("--client-id",default="demo")
    parser.add_argument("--include-legacy",action="store_true",help="also remove old rows without client_id")
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--confirm",default="",help="must equal DELETE-BETS when --apply is used")
    args=parser.parse_args()
    if args.apply and args.confirm!="DELETE-BETS":
        raise SystemExit("Refusing delete: use --apply --confirm DELETE-BETS")

    base=tenant_query(args.client_id,args.include_legacy)
    print("MODE:","APPLY" if args.apply else "DRY RUN")
    print("CLIENT:",args.client_id)
    print("USERS/SETTINGS/DEPOSITS/WITHDRAWALS: PRESERVED")

    total=0
    existing=set(raw.list_collection_names())
    for name in BET_COLLECTIONS:
        if name not in existing:continue
        count=raw[name].count_documents(base)
        total+=count
        print(f"{name}: {count}")
        if args.apply and count:raw[name].delete_many(base)

    wallet_query={"$and":[base,{"type":{"$in":list(GAME_TRANSACTION_TYPES)}}]}
    wallet_count=raw.wallet_transactions.count_documents(wallet_query) if "wallet_transactions" in existing else 0
    total+=wallet_count
    print(f"wallet_transactions(game only): {wallet_count}")
    if args.apply and wallet_count:raw.wallet_transactions.delete_many(wallet_query)

    if args.apply:
        # casino_rounds has historically been shared and may not contain a
        # client_id, so it is intentionally preserved to avoid cross-tenant deletion.
        print("DELETED:",total)
        print("casino_rounds preserved because legacy rows are not tenant-owned")
    else:
        print("WOULD DELETE:",total)
        print("Run again with --apply --confirm DELETE-BETS after checking counts")


if __name__=="__main__":main()

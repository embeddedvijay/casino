from __future__ import annotations

import argparse
from bson import ObjectId

from database import db


raw=getattr(db,"_raw",db)
DEFAULT_CLIENT="demo"
USER_OWNED=(
    "casino_bets","wallet_transactions","notifications","support_tickets",
    "deposit_payment_sessions","plinko_bets","chicken_road_bets",
    "teen_patti_rounds","andar_bahar_rounds",
)
CLIENT_OWNED=("game_settings","casino_settings","payment_settings","promotions","matka_markets","matka_timings","star_lines")


def find_user(row):
    ref=row.get("user_ref")
    if isinstance(ref,ObjectId):
        user=raw.users.find_one({"_id":ref})
        if user:return user
    value=str(row.get("user_id") or row.get("Contact") or row.get("username") or "").strip()
    choices=[{"user_id":value},{"username":value},{"mobile":value}]
    if ObjectId.is_valid(value):choices.append({"_id":ObjectId(value)})
    return raw.users.find_one({"$or":choices}) if value else None


def migrate(apply=False):
    report={}
    missing_users={"client_id":{"$in":[None,""]}}
    report["users_missing_client"]=raw.users.count_documents(missing_users)
    if apply:raw.users.update_many(missing_users,{"$set":{"client_id":DEFAULT_CLIENT}})
    for name in USER_OWNED:
        if name not in raw.list_collection_names():continue
        collection=raw[name];changed=0;unresolved=0
        for row in collection.find({"$or":[{"client_id":{"$exists":False}},{"client_id":None},{"client_id":""},{"user_ref":{"$exists":False}}]}):
            user=find_user(row)
            if not user:unresolved+=1;continue
            values={"client_id":str(user.get("client_id") or DEFAULT_CLIENT),"user_ref":user["_id"],"user_id":str(user["_id"])}
            if row.get("user_id") and str(row.get("user_id"))!=values["user_id"]:values["requested_user_id"]=str(row["user_id"])
            if apply:collection.update_one({"_id":row["_id"]},{"$set":values})
            changed+=1
        report[name]={"migratable":changed,"unresolved":unresolved}
    for name in CLIENT_OWNED:
        if name not in raw.list_collection_names():continue
        query={"client_id":{"$in":[None,""]}}
        count=raw[name].count_documents(query)
        if apply and count:raw[name].update_many(query,{"$set":{"client_id":DEFAULT_CLIENT}})
        report[name]={"defaulted":count}
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Backfill tenant ownership without deleting data")
    parser.add_argument("--apply",action="store_true",help="write changes; without this flag the command is a dry run")
    args=parser.parse_args()
    result=migrate(args.apply)
    print("MODE:","APPLY" if args.apply else "DRY RUN")
    for key,value in result.items():print(key,":",value)

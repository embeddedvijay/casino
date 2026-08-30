from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

import os
from database import client,db


raw=getattr(db,"_raw",db)
DATE_COLLECTION=re.compile(r"^\d{2}-\d{2}-\d{2}$")


def main():
    parser=argparse.ArgumentParser(description="Copy legacy CASINO_<client>/<date> Matka plays into matka_bets/<date>")
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    base_name=raw.name
    target_database=client[os.getenv("MATKA_BETS_DB_NAME","matka_bets")]
    client_ids=[str(row["client_id"]) for row in raw.clients.find({"client_id":{"$exists":True}},{"client_id":1})]
    copied=0
    print("MODE:","APPLY" if args.apply else "DRY RUN")
    for client_id in sorted(set(client_ids)):
        source=client[f"{base_name}_{client_id.lower()}"]
        for date_name in source.list_collection_names():
            if not DATE_COLLECTION.match(date_name):continue
            rows=list(source[date_name].find({}))
            print(f"{source.name}.{date_name} -> {target_database.name}.{date_name}: {len(rows)}")
            if not args.apply:continue
            target=target_database[date_name]
            target.create_index([("client_id",1),("Contact",1),("CreatedAt",-1)],name="client_contact_latest")
            for row in rows:
                row["Client"]=str(row.get("Client") or client_id)
                row["client_id"]=str(row.get("client_id") or client_id)
                row["game_date"]=str(row.get("Date") or date_name)
                target.replace_one({"_id":row["_id"]},row,upsert=True)
                copied+=1
    print("COPIED:",copied if args.apply else "dry-run only")
    print("Legacy databases are preserved for rollback and are not deleted.")


if __name__=="__main__":main()

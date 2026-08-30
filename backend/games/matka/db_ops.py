from copy import deepcopy
import os
import pymongo 
import traceback
import datetime
import time
from bson.objectid import ObjectId
import sys
import yaml
try:
    from .constant import main_num_list,MARKET_TIME_TABLE,WIN_RATES
except Exception:
    from hla_adv.hla_beta.constant import main_num_list,MARKET_TIME_TABLE,WIN_RATES
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

MONGO_URL=os.getenv("MATKA_MONGO_URI") or os.getenv("MONGO_URI") or os.getenv("MONGO_LOCAL_URL") or "mongodb://localhost:27017/"
CASINO_DB_NAME=os.getenv("CASINO_DB_NAME",os.getenv("DB_NAME","casino"))
MATKA_BETS_DB_NAME=os.getenv("MATKA_BETS_DB_NAME","matka_bets")
DEFAULT_CLIENT_ID=os.getenv("DEFAULT_CLIENT_ID","demo")

myclient=pymongo.MongoClient(MONGO_URL,maxPoolSize=int(os.getenv("MONGO_MAX_POOL_SIZE","20")),serverSelectionTimeoutMS=5000,appname="gold365-matka")
casino_db=myclient[CASINO_DB_NAME]

def get_game_date():
    current_date_time=datetime.datetime.now()
    if current_date_time.time()<datetime.time(1,0,0):
        current_date_time=current_date_time-datetime.timedelta(days=1)
    return current_date_time.strftime("%y-%m-%d")

def get_client_db_name(client_id=None):
    client_id=(client_id or DEFAULT_CLIENT_ID).lower()
    return f"{CASINO_DB_NAME}_{client_id}"

def get_matka_db(client_id=None):
    return myclient[get_client_db_name(client_id)]

def get_play_collection(client_id=None):
    # One shared Matka database with date-wise collections. Multi-tenant
    # ownership remains in each document's Client/client_id fields.
    return myclient[MATKA_BETS_DB_NAME][get_game_date()]

def get_play_collection_by_date(date_key):
    return myclient[MATKA_BETS_DB_NAME][str(date_key)]

def get_users_collection(client_id=None):
    return casino_db["users"]

def get_clients_collection():
    return casino_db["clients"]

def get_win_rates(client_id=None):
    client_id=str(client_id or DEFAULT_CLIENT_ID)
    saved=casino_db["matka_win_rates"].find_one({"client_id":client_id},{"_id":0}) or {}
    return {
        "ANK":int(saved.get("ank",round(WIN_RATES["ANK"]))),
        "Jodi":int(saved.get("jodi",WIN_RATES["Jodi"])),
        "SP":int(saved.get("sp",WIN_RATES["SP"])),
        "DP":int(saved.get("dp",WIN_RATES["DP"])),
        "TP":int(saved.get("tp",WIN_RATES["TP"])),
        "HS":int(saved.get("half_sangam",WIN_RATES["HS"])),
        "FS":int(saved.get("full_sangam",WIN_RATES["FS"])),
    }

current_date_time=datetime.datetime.now()
date=get_game_date()
db_frame=get_matka_db(DEFAULT_CLIENT_ID)
db=get_play_collection(DEFAULT_CLIENT_ID)

OFFER_TEXT = (
    "🔥 *Special Offer For You!* 🔥\n\n"
    "Aaj hi play karein aur paayein *extra bonus* 🎁\n"
    "Offer limited time ke liye hai ⏳\n\n"
    "👉 Abhi join karein!"
)

###############################################
# Single Mongo connection. Old function names are kept for compatibility.
def connect_to_cluster():
    print("Single Mongo connection ready")
    return myclient

def connect_to_cluster2():
    print("Second cluster disabled. Using single Mongo connection only.")
    return myclient

cluster=myclient
cluster2=myclient

def send_data1(data:dict):
    return True

def send_data2(data:dict):
    return True

def send_data(data:dict):
    return True

def get_users_name()->dict:
    global cluster
    clients = get_users_collection(DEFAULT_CLIENT_ID)
    client_names = clients.aggregate(
        [
            {
                "$match": {
                    "telegram_id" : {"$exists":True},
                    "name" : {"$exists":True}
                }
            },
            {
                "$group":{
                    "_id":None,
                    "Users" : {
                        "$push":{
                            "k":{"$toString":"$telegram_id"},
                            "v":"$name"
                        }
                    }
                }
            },
            {
                "$replaceRoot":{
                    "newRoot": {"$arrayToObject":"$Users"}
                }
            }
        ]
    ).to_list()
    if client_names:
        client_names = client_names[0]
        return client_names
    return {}


def get_users_play_win()->str:
    global cluster
    play = get_play_collection(DEFAULT_CLIENT_ID)

    play_win = play.aggregate(
        [
            {
                "$match":{
                    "Date" : date,
                    "Total" : {"$exists" : True}
                }
            },
            {
                "$group":{
                    "_id" :"$Contact",
                    "Play" : {"$sum":"$Total"},
                    "Win" : {"$sum":"$Win_Amt"}
                }
            }
        ]
    ).to_list()
    res = str()
    if play_win:
        user_names = get_users_name()
        for play in play_win:
            res += f'\n{user_names.get(play["_id"],play["_id"])} : {play["Play"]}/{play["Win"]}'
    return res

async def tele_get_users_play_win(update, context):
    q = update.callback_query
    await q.answer()

    result_text = get_users_play_win()

    if not result_text:
        result_text = "_No user play/win data found for today._"

    await q.from_user.send_message(
        result_text,
        parse_mode="Markdown"
    )

def get_client_play_win()->str:
    global cluster
    play = get_play_collection(DEFAULT_CLIENT_ID)

    play_win = play.aggregate(
        [
            {
                "$match":{
                    "Date" : date,
                    "Total" : {"$exists" : True}
                }
            },
            {
                "$group":{
                    "_id" :"$Market",
                    "Play" : {"$sum":"$Total"},
                    "Win" : {"$sum":"$Win_Amt"}
                }
            }
        ]
    ).to_list()
    res = str()
    if play_win:
        market_data = {}
        for row in play_win:
            market_data[row["_id"]] = {
                "PLAY": row.get("Play", 0),
                "WIN": row.get("Win", 0)
            }

        for k in MARKET_TIME_TABLE.keys():
            if k in market_data:
                res += (
                    f"\n{k}"
                    f"\n  PLAY : {market_data[k]['PLAY']}"
                    f"\n  WIN  : {market_data[k]['WIN']}\n"
                )
    return res

async def tele_get_client_play_win(update, context):
    q = update.callback_query
    await q.answer()

    result_text = get_client_play_win()

    if not result_text:
        result_text = "_No play / win data found for today._"

    await q.from_user.send_message(
        result_text
    )



def get_active_users()->list:
    """
    Returns list of active telegram_id in last 3 days
    """
    global cluster
    play = get_play_collection(DEFAULT_CLIENT_ID)
    active_ids = set()
    for i in range(0,3):
        _date = current_date_time - datetime.timedelta(days = i)
        _date = _date.strftime("%y-%m-%d")
        plays = play.distinct("Contact",{"Date":_date})
        if plays:
            active_ids.update(plays)
    return list(active_ids)

async def tele_get_active_users(update, context):
    q = update.callback_query
    await q.answer()

    active_list = get_active_users()

    if active_list:
        message = "\n".join(f"• `{uid}`" for uid in active_list)
    else:
        message = "_No active users found in last 3 days._"

    await q.from_user.send_message(
        message,
        parse_mode="Markdown"
    )




def get_inactive_users()->list:
    """
    Returns list of in-active telegram_id in last 3 days
    """
   
    active_users = get_active_users()
    user_names = get_users_name()
    inactive_users = set()
    for k,v in user_names.items():
        if k not in active_users:
            inactive_users.add(k)
    return list(inactive_users)

async def tele_get_inactive_users(update, context):
    q = update.callback_query
    await q.answer()

    inactive_list = get_inactive_users()

    if inactive_list:
        message = "\n".join(f"• `{uid}`" for uid in inactive_list)
    else:
        message = "_No inactive users found in last 3 days._"

    await q.from_user.send_message(
        message,
        parse_mode="Markdown"
    )

async def tele_send_offer_inactive_users(update, context):
    q = update.callback_query
    await q.answer("Sending offer to inactive users...")

    inactive_users = get_inactive_users()

    if not inactive_users:
        await q.from_user.send_message(
            "_No inactive users found._",
            parse_mode="Markdown"
        )
        return

    sent = 0
    failed = 0

    for user_id in inactive_users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=OFFER_TEXT,
                parse_mode="Markdown"
            )
            sent += 1
        except Exception as e:
            failed += 1
            # optional: log error
            # print(f"Failed to send to {user_id}: {e}")

    # ✅ Admin ko summary
    await q.from_user.send_message(
        f"✅ Offer sent successfully\n\n"
        f"📨 Sent : {sent}\n"
        f"❌ Failed : {failed}"
    )


################## for contact cutting ############

def get_contact_cutting(client_name:str)->dict:
    contact_cutting = {}
    with open('config.yaml','r') as file:
        config = yaml.safe_load(file)

    for client in config['clients']:
        if client_name != client['client_name']:
            continue
        for session in client['sessions']:
            for contact in session["in_contacts"]:
                contactData = contact.split('^')
                if len(contactData) > 1:
                    contact_cutting[contactData[0].strip()] = int(contactData[1])
                else:
                    contact_cutting[contactData[0].strip()] = 100
    return contact_cutting
####################################################


################################## Returns Boolean #######################################
def add_data(data:dict,cluster=True):
    '''
    Docstring for add_data
    
    :param data: Description
    :type data: dict
    :param cluster: Description

    compulsory fields
    {
        "Client": "",
        "Contact" : "",
        "Time" : "",
        "Message" : "",
        "Message_ID" : "",
        "Market" : "MILAN_NIGHT_CL",
        "Action" : "✅",
        "Result" : "[["123","456",50],["1","2",50]],
        "Total" : 250,
        "Settled" : False,
        "Analysis" : {},
        "dynamic_validation" : True,
    }
    '''
    try:
        print("==============================================================================",flush= True)

        client_id=data.get("Client",DEFAULT_CLIENT_ID)
        play_db=get_play_collection(client_id)
        data["Date"]=get_game_date()
        data["CreatedAt"]=datetime.datetime.utcnow()
        inserted_id=play_db.insert_one(data).inserted_id
        data["inserted_id"]=inserted_id
        if cluster:
            send_data(data)

        token = '{'
        p = ''
        for name,val in data.items():
            #print(f"{name} : {val}",flush=True)
            p += f"{name} : {val}\n"
            #print(f"{repr(name)} : {repr(val)},{type(val)}")
            if isinstance(val,str):
                token += f'"{name}":"{repr(val)[1:-1]}",'
            elif isinstance(val,ObjectId):
                token += f'"{name}":"{val}",'
            elif isinstance(val,bool):
                token += f'"{name}":{str(val).lower()},'
            else:
                safe_val = repr(val).replace("'", '"')
                token += f'"{name}":{safe_val}'

        
        print(f"{p}---------------------------------------------------------------------------",flush=True)
        time.sleep(0.05)
        sys.stdout.flush()
        
        token = token[:-1] + '}'
        print(token)
        sys.stdout.flush()
        return True
    except:
        print(f"\n\n Failure to Add Data to DB \n Data \n {data} ")
        traceback.print_exc()
        return False

def cancel_check(result_list:list,market_name:str, client_name:str,contact_name:str):
    present_data = get_client_table(client_name,market_name,contact_name=contact_name)
    check = True
    for sl in result_list:
        if(not all(present_data[n] >= int(sl[-1]) for n in sl[:-1])):
            check = False

    if(check):
        for i in range(len(result_list)):
            result_list[i][-1] = -int(result_list[i][-1])
        return result_list

    return False


################################## Returns Data #######################################

def get_client_table(client_name:str,market_name:str,contact_name = {"$exists":True},settled=False,to_settle= False,c_settled=False,to_csettle=False):

    play_db=get_play_collection(client_name)
    data = play_db.aggregate([
        {
            "$match":{
                "Client" : client_name,
                "Contact" : contact_name,
                "Market" : market_name,
                "Total" : {"$exists":True},
                "Settled" : settled,
                "CSettled":{"$exists":c_settled}
            }
        },
        {
            "$group":{
                "_id" : 0,
                "Transactions":{
                    "$push" : "$Result"
                },
                "object_ids":{
                    "$push":"$_id"
                },
            }
        },
    ])
    num_dict = {key:int(0) for key in main_num_list}
    for doc in data:
        transactions = doc["Transactions"]
        for sl in transactions:
            for l in sl:
                for n in l[:-1]:
                    if n in num_dict.keys():
                        num_dict[n] += int(l[-1])
                    else:
                        num_dict[n] = int(l[-1])


        if(to_settle):
            try:
                settle_client_result(doc["object_ids"])
            except:
                print(f"Failure To Settle Data of client_name:{client_name}, market_name:{market_name}")
                traceback.print_exc()
        if(to_csettle):
            try:
                close_market_open_settle(doc["object_ids"])
            except:
                print(f"Failure To CSettle Data of client_name:{client_name}, market_name:{market_name},")
                traceback.print_exc()
    
    return num_dict

def get_client_contacts(client_name:str):
    play_db=get_play_collection(client_name)
    data = play_db.aggregate([
        {
            "$match": {
                "Client": client_name
            }
        }, 
        {
            "$group": {
                "_id": 0, 
                "Contacts": {
                    "$addToSet": "$Contact"
                }
            }
        }
    ])
    for doc in data:
        return list(doc["Contacts"])
    return []


def get_client_play(client_name:str,contact_name:str,market_name:str):
    play_db=get_play_collection(client_name)
    data = play_db.aggregate([
        {
            "$match":{
                "Client" : client_name,
                "Contact" : contact_name,
                "Market" : market_name,
                "Total" : {"$exists":True},
            }
        },
        {
            "$group":{
                "_id" : 0,
                "SUM":{
                    "$sum" : "$Total"
                },
            }
        },
    ])
    for doc in data:
        return doc['SUM']
    return 0


def get_message_count(client_name:str,contact:str):
    play_db=get_play_collection(client_name)
    data = play_db.aggregate([
        {
            "$match":{
                "Client" : client_name,
                "Contact":contact,
                "Action":{"$regex":"✅"}
            }
        },
        {
            "$project":{
                "_id":0,
                "Action":1
            }
        }
    ])
    return len(list(data))

def get_all_message_id(client_name:str,contact:str)->set:
    play_db=get_play_collection(client_name)
    data = play_db.find(
        {
            "Client" : client_name,
            "Contact":contact,
            "Message_ID":{"$exists":True}
        },
        {
            "_id":0,
            "Message_ID":1
        }
    ).sort({"Time":1})
    ids = set()
    for doc in data:
        ids.add(doc['Message_ID'])
    return ids

def get_result_of_market(market:str,client_name=DEFAULT_CLIENT_ID):
    play_db=get_play_collection(client_name)
    data  = play_db.find_one({
        "Result" : True,
        market : {"$exists":True}
    })
    if data:
        return data[market]
    return data


def update_plays(res_doc:dict):
    global cluster
    #print(res_doc)
    current_date_time = datetime.datetime.now()
    if(current_date_time.time() < datetime.time(1,50,0)):
        date = current_date_time - datetime.timedelta(days = 1)
        date = date.strftime("%y-%m-%d")
    else:
        date = current_date_time.strftime("%y-%m-%d")
    #date = "25-04-27"

    try:
        for client in ["tele_admin"]:
            client = client.lower()
            rates=get_win_rates(client)
            plays_cur = get_play_collection(client).find({
                "Date":date,
                "Client":client,
                "Total":{"$exists":True}
            })
            plays = []

            for play in plays_cur:
                plays.append(play)
                try:
                    new = deepcopy(plays[-1])
                    new.pop("_id", None) 
                    if new.get('Win',False):
                        del new["Win"]
                    if new.get("Win_Amt",False):
                        del new["Win_Amt"]
                    
                    get_play_collection(client).find_one_and_replace(
                        {
                            "inserted_id" : new["inserted_id"],
                        },
                        new,
                        upsert= True
                    )
                except:
                    print("fail")
                    print(traceback.print_exc())
            

            for k,v in res_doc.items():
                if not isinstance(v,dict):
                    continue
                #open-> ank panal
                #print(client,k)
                if "OPEN" in v.keys():
                    OP_Ank = v["OPEN"]
                    OP_Panal = v["OPANAL"]
                    Jodi = False
                    FS = False
                    HSA = False
                    HSB = False

                    if v.get("CLOSE",False):
                        Jodi = v["OPEN"] + v["CLOSE"]
                        FS = f'{v["OPANAL"]}-{v["CPANAL"]}'
                        HSA = f'{v["OPANAL"]}-{v["CLOSE"]}'
                        HSB = f'{v["OPEN"]}-{v["CPANAL"]}'

                    match len(list(set([x for x in OP_Panal]))):
                        case 1:
                            Panal_price = rates['TP']
                        case 2:
                            Panal_price = rates['DP']
                        case _:
                            Panal_price = rates['SP']

                    for play in plays:
                        win = {
                            OP_Ank : 0,
                            OP_Panal : 0,
                            "Jodi" : 0,
                            "FS" : 0,
                            "HSA" : 0,
                            "HSB" : 0
                        }
                        win_amt = 0
                        if play["Market"] == (k+"_OP"):
                            #print(play)
                            for res_ls in play["Result"]:
                                if OP_Ank in res_ls[:-1]:
                                    win[OP_Ank] += int(res_ls[-1])
                                if OP_Panal in res_ls[:-1]:
                                    win[OP_Panal] += int(res_ls[-1] )
                                if Jodi and Jodi.strip() in res_ls[:-1]:
                                    win["Jodi"] += int(res_ls[-1] )
                                if FS and FS.strip() in res_ls[:-1]:
                                    win["FS"] += int(res_ls[-1] )
                                if HSA and HSA.strip() in res_ls[:-1]:
                                    win["HSA"] += int(res_ls[-1] )
                                if HSB and HSB.strip() in res_ls[:-1]:
                                    win["HSB"] += int(res_ls[-1] )
                                
                            win_amt = int(win[OP_Ank]*rates['ANK'])+int(win[OP_Panal]*Panal_price)+int(win["Jodi"]*rates['Jodi'])+int(win["FS"]*rates['FS'])+int(win["HSA"]*rates['HS'])+int(win["HSB"]*rates['HS'])
                            get_play_collection(client).find_one_and_update(
                                {
                                    "inserted_id" : play["inserted_id"],
                                },
                                {"$set":{"Win":win,"Win_Amt":win_amt}},
                                upsert= True
                            )
                #close-> jodi ank,panal
                if "CLOSE" in v.keys():
                    CL_Ank = v["CLOSE"]
                    CL_Panal = v["CPANAL"]

                    match len(list(set([x for x in CL_Panal]))):
                        case 1:
                            Panal_price = rates['TP']
                        case 2:
                            Panal_price = rates['DP']
                        case _:
                            Panal_price = rates['SP']
                            
                    for play in plays:
                        win = {
                            CL_Ank : 0,
                            CL_Panal : 0
                        }
                        win_amt = 0
                        if play["Market"] == (k+"_CL"):
                            for res_ls in play["Result"]:
                                if CL_Ank in res_ls[:-1]:
                                    win[CL_Ank] += int(res_ls[-1])
                                if CL_Panal in res_ls[:-1]:
                                    win[CL_Panal] += int(res_ls[-1])
                                
                            win_amt = int(win[CL_Ank]*rates['ANK'])+int(win[CL_Panal]*Panal_price)
                            get_play_collection(client).find_one_and_update(
                                {
                                    "inserted_id" : play["inserted_id"],
                                },
                                {"$set":{"Win":win,"Win_Amt":win_amt}},
                                upsert= True
                            )
    except:

        traceback.print_exc()
        #cluster = connect_to_cluster()
        #update_plays(res_doc)





################################## Update Data #######################################
def settle_client_result(object_ids:list,client_name=DEFAULT_CLIENT_ID):
    play_db=get_play_collection(client_name)
    result = play_db.update_many(
            {
                "_id" : {
                    "$in" : object_ids
                }
            },
            {
                "$set":{
                    "Settled": True
                }
            }
        )

def close_market_open_settle(object_ids:list,client_name=DEFAULT_CLIENT_ID):
    play_db=get_play_collection(client_name)
    result = play_db.update_many(
            {
                "_id" : {
                    "$in" : object_ids
                }
            },
            {
                "$set":{
                    "CSettled": True,
                }
            },
            upsert=True
        )

import mongomock
import pytest

import core.casino as casino


@pytest.fixture()
def raw_db(monkeypatch):
    database=mongomock.MongoClient().casino
    monkeypatch.setattr(casino,"db",database)
    casino.ensure_casino_indexes()
    database.clients.insert_one({"client_id":"demo","status":"active","maintenance_mode":False})
    return database


def add_user(database,username="real",balance=1000,is_demo=False,client_id="demo"):
    return database.users.insert_one({"client_id":client_id,"username":username,"user_id":username,"balance":balance,"status":"active","is_demo":is_demo,"role":"demo" if is_demo else "user"}).inserted_id


def test_real_user_bet_debits_wallet(raw_db):
    add_user(raw_db)
    bet=casino.place_bet(game="aviator",round_id="A-1",user_id="real",amount=100,position_key="seat:1")
    assert bet["status"]=="active"
    assert raw_db.users.find_one({"username":"real"})["balance"]==900
    assert raw_db.wallet_transactions.count_documents({"type":"game_bet"})==1


def test_demo_bet_never_changes_wallet(raw_db):
    add_user(raw_db,"demo",1000,True)
    casino.place_bet(game="aviator",round_id="A-1",user_id="demo",amount=999999,position_key="seat:1")
    assert raw_db.users.find_one({"username":"demo"})["balance"]==1000
    assert raw_db.wallet_transactions.count_documents({})==0


def test_duplicate_bet_is_rejected_without_second_debit(raw_db):
    add_user(raw_db)
    casino.place_bet(game="dragon-tiger",round_id="D-1",user_id="real",amount=50,position_key="dragon")
    with pytest.raises(casino.CasinoError) as error:
        casino.place_bet(game="dragon-tiger",round_id="D-1",user_id="real",amount=50,position_key="dragon")
    assert error.value.code=="duplicate_bet"
    assert raw_db.users.find_one({"username":"real"})["balance"]==950


def test_settlement_is_idempotent(raw_db):
    add_user(raw_db)
    bet=casino.place_bet(game="aviator",round_id="A-2",user_id="real",amount=100,position_key="seat:1")
    first=casino.settle_bet(bet["id"],250,{"multiplier":2.5})
    second=casino.settle_bet(bet["id"],250,{"multiplier":2.5})
    assert first["status"]=="won"
    assert second is None
    assert raw_db.users.find_one({"username":"real"})["balance"]==1150
    assert raw_db.wallet_transactions.count_documents({"type":"game_win"})==1


def test_clear_refunds_real_user_once(raw_db):
    add_user(raw_db)
    casino.place_bet(game="matka",round_id="M-1",user_id="real",amount=125,position_key="7")
    assert casino.cancel_user_bets("matka","M-1","real")==1
    assert casino.cancel_user_bets("matka","M-1","real")==0
    assert raw_db.users.find_one({"username":"real"})["balance"]==1000


def test_restart_recovery_refunds_open_real_bet(raw_db):
    add_user(raw_db)
    casino.place_bet(game="lucky-race",round_id="L-1",user_id="real",amount=200,position_key="car-1")
    casino.open_round("lucky-race","L-1")
    result=casino.recover_interrupted_games()
    assert result=={"cancelled_bets":1,"refunded_bets":1,"aborted_rounds":1}
    assert raw_db.users.find_one({"username":"real"})["balance"]==1000
    assert casino.recover_interrupted_games()=={"cancelled_bets":0,"refunded_bets":0,"aborted_rounds":0}


def test_same_username_is_isolated_between_clients(raw_db):
    raw_db.clients.insert_one({"client_id":"casino-b","status":"active"})
    add_user(raw_db,"same-mobile",1000,client_id="demo")
    add_user(raw_db,"same-mobile",700,client_id="casino-b")
    first=casino.place_bet(game="aviator",round_id="TENANT-1",user_id="same-mobile",client_id="demo",amount=100,position_key="seat:1")
    second=casino.place_bet(game="aviator",round_id="TENANT-1",user_id="same-mobile",client_id="casino-b",amount=50,position_key="seat:1")
    assert first["client_id"]=="demo"
    assert second["client_id"]=="casino-b"
    assert raw_db.users.find_one({"client_id":"demo","username":"same-mobile"})["balance"]==900
    assert raw_db.users.find_one({"client_id":"casino-b","username":"same-mobile"})["balance"]==650
    assert raw_db.casino_bets.count_documents({"client_id":"demo"})==1
    assert raw_db.casino_bets.count_documents({"client_id":"casino-b"})==1

"""Global demo-wallet policy for every game using the shared Mongo `db` object.

Production requests pass through unchanged. For a demo user, balance predicates
are removed and balance debit/credit mutations are stripped, while the rest of
the game/round update still runs normally.
"""
from copy import deepcopy

DEMO_NAMES={"demo","demo123"}
MONEY_FIELDS={"balance","wallet_balance","main_balance","available_balance","coins"}
IDENTITY_FIELDS=("user_id","username","user_name","client_id","name")

class UnlimitedDemoAmount(float):
    """Displays the stored demo value but never fails an amount comparison."""
    def __lt__(self,other): return False
    def __le__(self,other): return False
    def __gt__(self,other): return True
    def __ge__(self,other): return True
    def __sub__(self,other): return self
    def __add__(self,other): return self
    def __radd__(self,other): return self

def _demo_document(doc):
    if not isinstance(doc,dict): return doc
    is_demo=bool(doc.get("is_demo") or any(str(doc.get(k,"")).lower() in DEMO_NAMES for k in IDENTITY_FIELDS))
    if not is_demo:return doc
    doc=deepcopy(doc)
    for key in MONEY_FIELDS:
        if isinstance(doc.get(key),(int,float)): doc[key]=UnlimitedDemoAmount(doc[key])
    return doc

def _contains_demo(value):
    if isinstance(value,dict): return any(_contains_demo(v) for v in value.values())
    if isinstance(value,(list,tuple)): return any(_contains_demo(v) for v in value)
    return str(value or "").strip().lower() in DEMO_NAMES

def _without_money_filter(value):
    if isinstance(value,list):
        return [x for x in (_without_money_filter(v) for v in value) if x not in ({},None)]
    if not isinstance(value,dict): return value
    out={}
    for key,val in value.items():
        if key in MONEY_FIELDS: continue
        cleaned=_without_money_filter(val)
        if key in ("$and","$or") and not cleaned: continue
        out[key]=cleaned
    return out

def _without_money_update(update):
    out=deepcopy(update)
    for operator in ("$inc","$set","$setOnInsert","$min","$max"):
        values=out.get(operator)
        if isinstance(values,dict):
            for key in list(values):
                if key.split(".")[-1] in MONEY_FIELDS: values.pop(key,None)
            if not values: out.pop(operator,None)
    # Keep a legal no-op update if the original operation was money-only.
    if not out: out={"$set":{"_demo_wallet_untouched":True}}
    return out

class DemoAwareCollection:
    def __init__(self,raw,name=""): self._raw=raw; self._name=name
    def __getattr__(self,name): return getattr(self._raw,name)

    def _demo(self,query):
        if _contains_demo(query): return True
        try:
            doc=self._raw.find_one(_without_money_filter(query),{"is_demo":1,**{k:1 for k in IDENTITY_FIELDS}})
            return bool(doc and (doc.get("is_demo") or any(str(doc.get(k,"")).lower() in DEMO_NAMES for k in IDENTITY_FIELDS)))
        except Exception:return False

    def find_one_and_update(self,query,update,*args,**kwargs):
        if self._demo(query):
            query=_without_money_filter(query); update=_without_money_update(update)
        return _demo_document(self._raw.find_one_and_update(query,update,*args,**kwargs))

    def find_one(self,query,*args,**kwargs):
        return _demo_document(self._raw.find_one(query,*args,**kwargs))

    def update_one(self,query,update,*args,**kwargs):
        if self._demo(query):
            query=_without_money_filter(query); update=_without_money_update(update)
        return self._raw.update_one(query,update,*args,**kwargs)

    def find_one_and_replace(self,query,replacement,*args,**kwargs):
        if self._demo(query):
            current=self._raw.find_one(_without_money_filter(query)) or {}
            replacement=deepcopy(replacement)
            for key in MONEY_FIELDS:
                if key in current: replacement[key]=current[key]
            query=_without_money_filter(query)
        return self._raw.find_one_and_replace(query,replacement,*args,**kwargs)

class DemoAwareDatabase:
    def __init__(self,raw): self._raw=raw
    def __getattr__(self,name):
        value=getattr(self._raw,name)
        return DemoAwareCollection(value,name) if hasattr(value,"find_one_and_update") else value
    def __getitem__(self,name): return DemoAwareCollection(self._raw[name],name)

def wrap_database_for_demo(db):
    return db if isinstance(db,DemoAwareDatabase) else DemoAwareDatabase(db)

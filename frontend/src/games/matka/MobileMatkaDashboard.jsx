import React,{useEffect,useState}from"react";
import"./MobilematkaDashboard.css";
import UserMenuLayout from "../../shared/UserMenuLayout";
import{fetchCurrentUser}from"../../shared/userSession";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;

const gameGroups=[
  {
    title:"SRIDEVI",
    day:{key:"SRIDEVI_DAY",name:"SRIDEVI DAY",type:"day"},
    night:{key:"SRIDEVI_NIGHT",name:"SRIDEVI NIGHT",type:"night"}
  },
  {
    title:"TIME BAZAR",
    day:{key:"TIME_BAZAR_DAY",name:"TIME BAZAR DAY",type:"day"},
    night:{key:"MAIN_BAZAR_NIGHT",name:"MAIN BAZAR NIGHT",type:"night"}
  },
  {
    title:"MADHUR",
    day:{key:"MADHUR_DAY",name:"MADHUR DAY",type:"day"},
    night:{key:"MADHUR_NIGHT",name:"MADHUR NIGHT",type:"night"}
  },
  {
    title:"MILAN",
    day:{key:"MILAN_DAY",name:"MILAN DAY",type:"day"},
    night:{key:"MILAN_NIGHT",name:"MILAN NIGHT",type:"night"}
  },
  {
    title:"RAJDHANI",
    day:{key:"RAJDHANI_DAY",name:"RAJDHANI DAY",type:"day"},
    night:{key:"RAJDHANI_NIGHT",name:"RAJDHANI NIGHT",type:"night"}
  },
  {
    title:"SUPREME",
    day:{key:"SUPREME_DAY",name:"SUPREME DAY",type:"day"},
    night:{key:"SUPREME_NIGHT",name:"SUPREME NIGHT",type:"night"}
  },
  {
    title:"KALYAN",
    day:{key:"KALYAN_DAY",name:"KALYAN DAY",type:"day"},
    night:{key:"KALYAN_NIGHT",name:"KALYAN NIGHT",type:"night"}
  }
];

const market_schedule={
  Saturday:{RAJDHANI_NIGHT:false,KALYAN_NIGHT:false,MAIN_BAZAR_NIGHT:false},
  Sunday:{TIME_BAZAR_DAY:false,MILAN_DAY:false,RAJDHANI_DAY:false,KALYAN_DAY:false,MADHUR_NIGHT:false,MILAN_NIGHT:false,RAJDHANI_NIGHT:false,KALYAN_NIGHT:false,MAIN_BAZAR_NIGHT:false}
};

const market_flow=["SRIDEVI_DAY","TIME_BAZAR_DAY","MADHUR_DAY","MILAN_DAY","RAJDHANI_DAY","SUPREME_DAY","KALYAN_DAY","SRIDEVI_NIGHT","MADHUR_NIGHT","SUPREME_NIGHT","MILAN_NIGHT","RAJDHANI_NIGHT","KALYAN_NIGHT","MAIN_BAZAR_NIGHT"];

const possibleKeys=(key)=>{
  const base=key.replace("_OP","").replace("_CL","");
  return[key,`${base}_OP`,`${base}_CL`,base,base.replace("_DAY",""),base.replace("_NIGHT","")];
};

const getMarket=(results,key)=>{
  if(!results)return null;
  for(const k of possibleKeys(key)){
    if(results[k])return results[k];
  }
  return null;
};

const getValue=(market,keys,fallback="")=>{
  if(!market)return fallback;
  for(const key of keys){
    if(market[key]!==undefined&&market[key]!==null&&market[key]!=="")return String(market[key]);
  }
  return fallback;
};

const isRealResult=(value)=>{
  const v=value===undefined||value===null?"":String(value).trim();
  return v!==""&&v!=="*"&&v!=="**"&&v!=="-"&&v!=="--"&&v!==":--";
};

const getTodayName=()=>new Date().toLocaleDateString("en-US",{weekday:"long"});
const isMarketOff=(key)=>market_schedule[getTodayName()]?.[key]===false;

function MarketBox({game,market}){
  const off=isMarketOff(game.key);
  const open=getValue(market,["OPEN","open"],"*");
  const close=getValue(market,["CLOSE","close"],"*");
  const resultDone=isRealResult(open)&&isRealResult(close);
  const openTime=getValue(market,["OTIME","openTime","open_time"],"--:--");
  const closeTime=getValue(market,["CTIME","closeTime","close_time"],"--:--");
  const opana=getValue(market,["OPANAL","OPANA","OPENPANA","openPana","open_pana"],"***");
  const cpana=getValue(market,["CPANAL","CPANA","CLOSEPANA","closePana","close_pana"],"***");
  const result=off?"OFF":!isRealResult(open)&&!isRealResult(close)?"--":`${isRealResult(open)?open:"*"}${isRealResult(close)?close:"*"}`;
  const fullResult=isRealResult(open)&&isRealResult(close);
  const openMarketInput=()=>{
    if(off||fullResult)return;
    const marketName=market_flow.includes(game.key)?game.key:game.key;
    window.location.href=`/matka/market-input/${marketName}`;
  };
  return(
    <button className={`mb-market-box ${game.type} ${off||resultDone?"market-off":"blink-play"}`} onClick={openMarketInput}>
    <div className="mb-market-title">{game.name}</div>
      <div className="mb-market-body">
        <div className="mb-row">
          <i>◷</i>
          <span>OPEN</span>
          <strong>{openTime}</strong>
        </div>
        <div className="mb-row mk-result-row">
          <i>♛</i>
          <span>RESULT</span>
          <strong>{result}</strong>
          <em>{off?"OFF":`${opana} - ${cpana}`}</em>
        </div>
        <div className="mb-row">
          <i>◴</i>
          <span>CLOSE</span>
          <strong>{closeTime}</strong>
        </div>
      </div>
    </button>
  );
}

function MarketGroup({group,results}){
  return(
    <section className="mb-group-card">
      <h3>{group.title}</h3>
      <div className="mb-group-row">
        <MarketBox game={group.day} market={getMarket(results,group.day.key)}/>
        <MarketBox game={group.night} market={getMarket(results,group.night.key)}/>
      </div>
    </section>
  );
}

export default function MatkaDashboard(){
  const[resultDoc,setResultDoc]=useState(null);
  const[user,setUser]=useState({user_name:"DEMO123",balance:0});

  useEffect(()=>{
    const loadResults=()=>{
      fetch(`${API}/api/games/matka/results/latest`)
      .then((res)=>res.json())
      .then((data)=>setResultDoc(data))
      .catch(()=>setResultDoc(null));
    };
    loadResults();
    fetchCurrentUser().then(setUser);
    const interval=setInterval(loadResults,10000);
    return()=>clearInterval(interval);
  },[]);

  const results=resultDoc?.Result&&typeof resultDoc.Result==="object"?resultDoc.Result:resultDoc||{};

  return(
    <div className="mb-page">
      <header className="mb-top">
        <div className="mb-brand">
          <span>MATKA</span>
          <b>BOOK</b>
        </div>
        <div className="mb-profile">
          <button className="mk-info-btn" onClick={()=>window.location.href="/matka/info"}>ⓘ</button>
          <span className="balance">{Number(user.balance||0).toFixed(2)}</span>
          <UserMenuLayout/>
          <span className="user">{user.user_name||"DEMO123"}</span>
        </div>
      </header>

      <section className="mb-hero">
        <h1>MATKA BOOK</h1>
        <p>FAST RESULT • FAIR GAME • TRUSTED PLATFORM</p>
      </section>

      <main className="mb-list">
        {gameGroups.map((group)=>(
          <MarketGroup key={group.title} group={group} results={results}/>
        ))}
      </main>

      <div className="mb-help-bar">
        <span>ⓘ</span>
        <b>Game play k liye market ko select kre</b>
      </div>
    </div>
  );
}
import React,{useEffect,useState}from"react";
import"./matkaDashboard.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;

const games=[
  {key:"SRIDEVI_DAY",name:"SRIDEVI DAY"},
  {key:"SRIDEVI_NIGHT",name:"SRIDEVI NIGHT"},
  {key:"TIME_BAZAR_DAY",name:"TIME BAZAR DAY"},
  {key:"MAIN_BAZAR_NIGHT",name:"MAIN BAZAR NIGHT"},
  {key:"MADHUR_DAY",name:"MADHUR DAY"},
  {key:"MADHUR_NIGHT",name:"MADHUR NIGHT"},
  {key:"MILAN_DAY",name:"MILAN DAY"},
  {key:"MILAN_NIGHT",name:"MILAN NIGHT"},
  {key:"RAJDHANI_DAY",name:"RAJDHANI DAY"},
  {key:"RAJDHANI_NIGHT",name:"RAJDHANI NIGHT"},
  {key:"SUPREME_DAY",name:"SUPREME DAY"},
  {key:"SUPREME_NIGHT",name:"SUPREME NIGHT"},
  {key:"KALYAN_DAY",name:"KALYAN DAY"},
  {key:"KALYAN_NIGHT",name:"KALYAN NIGHT"}
];

const market_schedule={
  Saturday:{
    RAJDHANI_NIGHT:false,
    KALYAN_NIGHT:false,
    MAIN_BAZAR_NIGHT:false
  },
  Sunday:{
    TIME_BAZAR_DAY:false,
    MILAN_DAY:false,
    RAJDHANI_DAY:false,
    KALYAN_DAY:false,
    MADHUR_NIGHT:false,
    MILAN_NIGHT:false,
    RAJDHANI_NIGHT:false,
    KALYAN_NIGHT:false,
    MAIN_BAZAR_NIGHT:false
  }
};

const market_flow=[
  "SRIDEVI_DAY",
  "TIME_BAZAR_DAY",
  "MADHUR_DAY",
  "MILAN_DAY",
  "RAJDHANI_DAY",
  "SUPREME_DAY",
  "KALYAN_DAY",
  "SRIDEVI_NIGHT",
  "MADHUR_NIGHT",
  "SUPREME_NIGHT",
  "MILAN_NIGHT",
  "RAJDHANI_NIGHT",
  "KALYAN_NIGHT",
  "MAIN_BAZAR_NIGHT"
];

const possibleKeys=(key)=>{
  const base=key.replace("_OP","").replace("_CL","");
  return[
    key,
    `${base}_OP`,
    `${base}_CL`,
    base,
    base.replace("_DAY",""),
    base.replace("_NIGHT","")
  ];
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

const splitPana=(value)=>{
  const v=value===undefined||value===null||value===""?"***":String(value);
  return v.padEnd(3,"*").slice(0,3).split("");
};

const isRealResult=(value)=>{
  const v=value===undefined||value===null?"":String(value).trim();
  return v!==""&&v!=="*"&&v!=="**"&&v!=="-"&&v!=="--"&&v!==":--";
};

const getTodayName=()=>new Date().toLocaleDateString("en-US",{weekday:"long"});
const isMarketOff=(key)=>market_schedule[getTodayName()]?.[key]===false;

function MoneyRain({side}){
  return(
    <div className={`money-side ${side}`}>
      <div className="money-matka">🏺</div>
      {[...Array(22)].map((_,i)=><span key={i} className="money-coin" style={{"--i":i}}>₹</span>)}
      <div className="money-pile">●●●</div>
    </div>
  );
}

function ResultOverlay({game,market,index}){
  const off=isMarketOff(game.key);
  const open=getValue(market,["OPEN","open"],"*");
  const close=getValue(market,["CLOSE","close"],"*");
  const opana=getValue(market,["OPANAL","OPANA","OPENPANA","openPana","open_pana"],"***");
  const cpana=getValue(market,["CPANAL","CPANA","CLOSEPANA","closePana","close_pana"],"***");
  const openTime=getValue(market,["OTIME","openTime","open_time"],"--:--");
  const closeTime=getValue(market,["CTIME","closeTime","close_time"],"--:--");
  const fullResult=isRealResult(open)&&isRealResult(close);
  const disableMarket=off||fullResult;
  const result=off?"OFF":!isRealResult(open)&&!isRealResult(close)?"--":`${isRealResult(open)?open:"*"}${isRealResult(close)?close:"*"}`;
  const openMarketInput=()=>{
    if(disableMarket)return;
    const marketName=market_flow.includes(game.key)?game.key:game.key;
    window.location.href=`/matka/market-input/${marketName}`;
  };
  return(
    <div className={`mk-overlay-card card-${index}`}>
      <div className="mk-open-time">{openTime}</div>
      <div className={`mk-result-main ${disableMarket?"market-off":""}`}>
        {result}
        <small>{off?"MARKET CLOSED":`${splitPana(opana).join("")} - ${splitPana(cpana).join("")}`}</small>
      </div>
      <div className="mk-close-time">{closeTime}</div>
      <button disabled={disableMarket} className={`mk-play-now ${disableMarket?"result-done":"blink-play"}`} onClick={openMarketInput}>PLAY NOW</button>
    </div>
  );
}

export default function MatkaDashboard(){
  const[resultDoc,setResultDoc]=useState(null);

  useEffect(()=>{
    const loadResults=()=>{
      fetch(`${API}/api/games/matka/results/latest`)
        .then(res=>res.json())
        .then(data=>setResultDoc(data))
        .catch(()=>setResultDoc(null));
    };
    loadResults();
    const interval=setInterval(loadResults,10000);
    return()=>clearInterval(interval);
  },[]);

  const results=resultDoc?.Result&&typeof resultDoc.Result==="object"?resultDoc.Result:resultDoc||{};

  return(
    <div className="mk-page">
      <header className="mk-top">
        <div className="mk-brand">
          <span className="mk-home">⌂</span>
          <span>GOLD</span>
          <b>365</b>
        </div>
        <div className="mk-profile">
          <span>🌐</span>
          <span className="mk-balance">0.00</span>
          <span>☰</span>
          <span className="mk-user">DEM123</span>
        </div>
      </header>
      <MoneyRain side="left"/>
      <MoneyRain side="right"/>
      <div className="mk-board">
        {games.map((game,index)=><ResultOverlay key={game.key} game={game} index={index} market={getMarket(results,game.key)}/>)}
      </div>
    </div>
  );
}
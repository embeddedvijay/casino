import React,{useEffect,useState}from"react";
import"./matkaDashboard.css";

const API="http://localhost:8005";

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

const possibleKeys=(key)=>{
const base=key.replace("_OP","").replace("_CL","");
return[key,`${base}_OP`,`${base}_CL`,base,base.replace("_DAY",""),base.replace("_NIGHT","")];
};

const getMarket=(results,key)=>{
if(!results)return null;
for(const k of possibleKeys(key)){if(results[k])return results[k];}
return null;
};

const getValue=(market,keys,fallback="")=>{
if(!market)return fallback;
for(const key of keys){if(market[key]!==undefined&&market[key]!==null&&market[key]!=="")return String(market[key]);}
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

function MoneyRain({side}){
return <div className={`money-side ${side}`}><div className="money-matka">🏺</div>{[...Array(22)].map((_,i)=><span key={i} className="money-coin" style={{"--i":i}}>₹</span>)}<div className="money-pile">●●●</div></div>;
}

function ResultOverlay({game,market,index}){
const open=getValue(market,["OPEN","open"],"*");
const close=getValue(market,["CLOSE","close"],"*");
const opana=getValue(market,["OPANAL","OPANA","OPENPANA","openPana","open_pana"],"***");
const cpana=getValue(market,["CPANAL","CPANA","CLOSEPANA","closePana","close_pana"],"***");
const openTime=getValue(market,["OTIME","openTime","open_time"],"--:--");
const closeTime=getValue(market,["CTIME","closeTime","close_time"],"--:--");
const fullResult=isRealResult(open)&&isRealResult(close);
const result=!isRealResult(open)&&!isRealResult(close)?"--":`${isRealResult(open)?open:"*"}${isRealResult(close)?close:"*"}`;
return(
<div className={`mk-overlay-card card-${index}`}>
<div className="mk-open-time">{openTime}</div>
<div className="mk-result-main">{result}<small>{splitPana(opana).join("")} - {splitPana(cpana).join("")}</small></div>
<div className="mk-close-time">{closeTime}</div>
<button className={`mk-play-now ${fullResult?"result-done":"blink-play"}`} onClick={()=>window.location.href=`/matka/play/${game.key}`}>PLAY NOW</button>
</div>
);
}

export default function MatkaDashboard(){
const[resultDoc,setResultDoc]=useState(null);
const[status,setStatus]=useState("Loading");

useEffect(()=>{
const loadResults=()=>{
fetch(`${API}/api/games/matka/results/latest`).then(res=>res.json()).then(data=>{setResultDoc(data);setStatus("Live Result");}).catch(()=>{setResultDoc(null);setStatus("API Error");});
};
loadResults();
const interval=setInterval(loadResults,10000);
return()=>clearInterval(interval);
},[]);

const results=resultDoc?.Result&&typeof resultDoc.Result==="object"?resultDoc.Result:resultDoc||{};

return(
<div className="mk-page">
  <MoneyRain side="left"/>
  <MoneyRain side="right"/>
  <div className="mk-board">
    {games.map((game,index)=><ResultOverlay key={game.key} game={game} index={index} market={getMarket(results,game.key)}/>)}
  </div>
</div>
);
}
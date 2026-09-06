import React,{useEffect,useState}from "react";
import "./MobileMatkaInfo.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;

const rates=[
  ["ANK","10 KA 95"],
  ["JODI","10 KA 950"],
  ["SP","10 KA 1500"],
  ["DP","10 KA 3000"],
  ["TP","10 KA 7000"]
];

const DEFAULT_MARKET_TIMES=[
  ["SRIDEVI DAY","11:45 AM","12:45 PM"],
  ["TIME BAZAR DAY","01:10 PM","02:10 PM"],
  ["MADHUR DAY","01:35 PM","02:35 PM"],
  ["MILAN DAY","03:10 PM","05:10 PM"],
  ["RAJDHANI DAY","03:12 PM","05:12 PM"],
  ["SUPREME DAY","03:45 PM","05:45 PM"],
  ["KALYAN DAY","04:15 PM","06:15 PM"],
  ["SRIDEVI NIGHT","07:25 PM","08:25 PM"],
  ["MADHUR NIGHT","08:35 PM","10:35 PM"],
  ["SUPREME NIGHT","18:55 PM","10:55 PM"],
  ["MILAN NIGHT","09:10 PM","11:10 PM"],
  ["RAJDHANI NIGHT","09:35 PM","11:45 PM"],
  ["KALYAN NIGHT","09:40 PM","11:40 PM"],
  ["MAIN BAZAR NIGHT","09:53 PM","12:05 AM"]
];


const marketKey=(name)=>String(name||"").trim().toUpperCase().replace(/\s+/g,"_");
const formatTime=(value,fallback)=>{
  if(!value)return fallback;
  const match=String(value).match(/^(\d{1,2}):(\d{2})$/);
  if(!match)return String(value);
  const hour=Number(match[1]);
  return `${hour%12||12}:${match[2]} ${hour>=12?"PM":"AM"}`;
};

export default function MobileMatkaInfo(){
  const[marketTimes,setMarketTimes]=useState(DEFAULT_MARKET_TIMES);

  useEffect(()=>{
    fetch(`${API}/api/games/matka/markets`)
      .then((res)=>res.ok?res.json():Promise.reject())
      .then((data)=>{
        const list=Array.isArray(data)?data:Array.isArray(data?.markets)?data.markets:[];
        const config=Object.fromEntries(list.map((market)=>[String(market.key||marketKey(market.name)).toUpperCase(),market]));
        setMarketTimes(DEFAULT_MARKET_TIMES.map((row)=>{
          const market=config[marketKey(row[0])];
          return market?[row[0],formatTime(market.open_time,row[1]),formatTime(market.close_time,row[2])]:row;
        }));
      })
      .catch(()=>setMarketTimes(DEFAULT_MARKET_TIMES));
  },[]);

  return(
    <div className="mmi-page">
      <header className="mmi-top">
        <button onClick={()=>window.history.back()}>‹</button>
        <h2>GAME INFO</h2>
        <span>ⓘ</span>
      </header>

      <section className="mmi-hero">
        <h1>MATKA BOOK</h1>
        <p>Game rate aur market timing yahan dekhiye</p>
      </section>

      <section className="mmi-card">
        <h3>🎯 GAME RATE</h3>
        {rates.map((item,index)=>(
          <div className="mmi-rate" key={index}>
            <span>{item[0]}</span>
            <b>{item[1]}</b>
          </div>
        ))}
      </section>

      <section className="mmi-card">
        <h3>🕘 MARKET GAME TIME</h3>
        <div className="mmi-head">
          <span>MARKET</span>
          <span>OPEN</span>
          <span>CLOSE</span>
        </div>
        {marketTimes.map((item,index)=>(
          <div className="mmi-time" key={index}>
            <span>{item[0]}</span>
            <b>{item[1]}</b>
            <b>{item[2]}</b>
          </div>
        ))}
      </section>

      <section className="mmi-ad">
        <h2>PLAY MORE</h2>
        <h1>WIN MORE</h1>
        <p>Fast Result • Trusted Platform</p>
      </section>
    </div>
  );
}
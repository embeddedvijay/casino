import React,{useEffect,useState}from "react";
import "./MatkaInfo.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;

const gameRates=[
  ["SINGLE","10 KA 95"],
  ["JODI","10 KA 950"],
  ["SINGLE PATTI","10 KA 1500"],
  ["DOUBLE PATTI","10 KA 3000"],
  ["TRIPPLE PATTI","10 KA 7000"]
];

const marketRates=[
  ["OPEN","10 KA 95"],
  ["PANA","10 KA 150"],
  ["JODI","10 KA 950"],
  ["SINGLE PATTI (SP)","10 KA 1500"],
  ["DOUBLE PATTI (DP)","10 KA 3000"],
  ["TRIPPLE PATTI (TP)","10 KA 7000"]
];

const DEFAULT_MARKET_TIMES=[
  ["☀️","SRIDEVI DAY","11:45 AM","12:45 PM"],
  ["☀️","TIME BAZAR DAY","01:10 PM","02:10 PM"],
  ["☀️","MADHUR DAY","01:35 PM","02:35 PM"],
  ["☀️","MILAN DAY","03:10 PM","05:10 PM"],
  ["☀️","RAJDHANI DAY","03:12 PM","05:12 PM"],
  ["☀️","SUPREME DAY","03:45 PM","05:45 PM"],
  ["☀️","KALYAN DAY","04:15 PM","06:15 PM"],
  ["🌙","SRIDEVI NIGHT","07:25 PM","08:25 PM"],
  ["🌙","MADHUR NIGHT","08:35 PM","10:35 PM"],
  ["🌙","SUPREME NIGHT","18:55 PM","10:55 PM"],
  ["🌙","MILAN NIGHT","09:10 PM","11:10 PM"],
  ["🌙","RAJDHANI NIGHT","09:35 PM","11:45 PM"],
  ["🌙","KALYAN NIGHT","09:40 PM","11:40 PM"],
  ["🌙","MAIN BAZAR NIGHT","09:53 PM","12:05 AM"]
];

const marketKey=(name)=>String(name||"").trim().toUpperCase().replace(/\s+/g,"_");
const formatTime=(value,fallback)=>{
  if(!value)return fallback;
  const match=String(value).match(/^(\d{1,2}):(\d{2})$/);
  if(!match)return String(value);
  const hour=Number(match[1]);
  return `${hour%12||12}:${match[2]} ${hour>=12?"PM":"AM"}`;
};

export default function MatkaInfo(){
  const[marketTimes,setMarketTimes]=useState(DEFAULT_MARKET_TIMES);

  useEffect(()=>{
    fetch(`${API}/api/games/matka/markets`)
      .then((res)=>res.ok?res.json():Promise.reject())
      .then((data)=>{
        const list=Array.isArray(data)?data:Array.isArray(data?.markets)?data.markets:[];
        const config=Object.fromEntries(list.map((market)=>[String(market.key||marketKey(market.name)).toUpperCase(),market]));
        setMarketTimes(DEFAULT_MARKET_TIMES.map((row)=>{
          const market=config[marketKey(row[1])];
          return market?[row[0],row[1],formatTime(market.open_time,row[2]),formatTime(market.close_time,row[3])]:row;
        }));
      })
      .catch(()=>setMarketTimes(DEFAULT_MARKET_TIMES));
  },[]);

  return(
    <div className="mi-page">
      <div className="mi-top">
        <button onClick={()=>window.history.back()} className="mi-back">‹</button>
        <h2>MATKA <span>BOOK</span></h2>
        <div className="mi-user">
          <b>₹0.00</b>
          <strong>DEM123</strong>
        </div>
      </div>

      <section className="mi-hero">
        <div className="mi-pot">🏺</div>
        <div>
          <h1>MATKA INFORMATION</h1>
          <p>FAST RESULT • FAIR GAME • TRUSTED PLATFORM</p>
        </div>
        <div className="mi-num">852</div>
      </section>

      <section className="mi-rate-grid">
        <RateCard title="MATKA GAME RATES" data={gameRates}/>
        <RateCard title="MARKET GAME RATES" data={marketRates}/>
      </section>

      <section className="mi-time-card">
        <h3>🕘 ALL MARKETS GAME TIME</h3>
        <div className="mi-table">
          <div className="mi-head"><span>MARKET</span><span>OPEN TIME</span><span>CLOSE TIME</span></div>
          {marketTimes.map((row,i)=>(
            <div className="mi-tr" key={i}>
              <span><i>{row[0]}</i>{row[1]}</span>
              <span>{row[2]}</span>
              <span>{row[3]}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="mi-ad">
        <div>
          <h2>PLAY MORE<br/><span>WIN MORE!</span></h2>
          <p>FAST RESULT • BIG WINNINGS • FAIR GAME</p>
          <button>PLAY NOW</button>
        </div>
        <div className="mi-ad-pot">🏺</div>
      </section>
    </div>
  );
}

function RateCard({title,data}){
  return(
    <div className="mi-rate-card">
      <h3>🪙 {title}</h3>
      {data.map((item,i)=>(
        <div className="mi-rate-row" key={i}>
          <span>☞ {item[0]}</span>
          <b>{item[1]}</b>
        </div>
      ))}
    </div>
  );
}
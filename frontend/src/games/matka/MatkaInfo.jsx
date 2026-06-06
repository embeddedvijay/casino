import React from "react";
import "./MatkaInfo.css";

const gameRates=[
  ["SINGLE","10 KA 95"],
  ["JODI","10 KA 950"],
  ["SINGLE PATTI","10 KA 1400"],
  ["DOUBLE PATTI","10 KA 2800"],
  ["TRIPPLE PATTI","10 KA 8000"]
];

const marketRates=[
  ["OPEN","10 KA 95"],
  ["PANA","10 KA 150"],
  ["JODI","10 KA 950"],
  ["SINGLE PATTI (SP)","10 KA 1400"],
  ["DOUBLE PATTI (DP)","10 KA 2800"],
  ["TRIPPLE PATTI (TP)","10 KA 8000"]
];

const marketTimes=[
  ["☀️","SRIDEVI DAY","10:00 AM","12:00 PM"],
  ["☀️","TIME BAZAR DAY","11:30 AM","01:30 PM"],
  ["☀️","MADHUR DAY","01:00 PM","03:00 PM"],
  ["☀️","MILAN DAY","02:30 PM","04:30 PM"],
  ["☀️","RAJDHANI DAY","04:00 PM","06:00 PM"],
  ["☀️","SUPREME DAY","05:30 PM","07:30 PM"],
  ["☀️","KALYAN DAY","07:00 PM","09:00 PM"],
  ["🌙","SRIDEVI NIGHT","08:00 PM","10:00 PM"],
  ["🌙","MADHUR NIGHT","09:30 PM","11:30 PM"],
  ["🌙","SUPREME NIGHT","11:00 PM","01:00 AM"],
  ["🌙","MILAN NIGHT","12:30 AM","02:30 AM"],
  ["🌙","RAJDHANI NIGHT","02:00 AM","04:00 AM"],
  ["🌙","KALYAN NIGHT","03:30 AM","05:30 AM"],
  ["🌙","MAIN BAZAR NIGHT","05:00 AM","07:00 AM"]
];

export default function MatkaInfo(){
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
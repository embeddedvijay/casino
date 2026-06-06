import React from "react";
import "./MobileMatkaInfo.css";

const rates=[
  ["ANK","10 KA 95"],
  ["JODI","10 KA 950"],
  ["SP","10 KA 1400"],
  ["DP","10 KA 2800"],
  ["TP","10 KA 8000"]
];

const marketTimes=[
  ["SRIDEVI DAY","10:00 AM","12:00 PM"],
  ["TIME BAZAR DAY","11:30 AM","01:30 PM"],
  ["MADHUR DAY","01:00 PM","03:00 PM"],
  ["MILAN DAY","02:30 PM","04:30 PM"],
  ["RAJDHANI DAY","04:00 PM","06:00 PM"],
  ["SUPREME DAY","05:30 PM","07:30 PM"],
  ["KALYAN DAY","07:00 PM","09:00 PM"],
  ["SRIDEVI NIGHT","08:00 PM","10:00 PM"],
  ["MADHUR NIGHT","09:30 PM","11:30 PM"],
  ["SUPREME NIGHT","11:00 PM","01:00 AM"],
  ["MILAN NIGHT","12:30 AM","02:30 AM"],
  ["RAJDHANI NIGHT","02:00 AM","04:00 AM"],
  ["KALYAN NIGHT","03:30 AM","05:30 AM"],
  ["MAIN BAZAR NIGHT","05:00 AM","07:00 AM"]
];

export default function MobileMatkaInfo(){
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
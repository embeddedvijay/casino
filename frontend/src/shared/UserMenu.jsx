import React from "react";
import "./UserMenu.css";

const userMenuItems=[
{icon:"💰",title:"Deposit",line1:"Add funds to your wallet",line2:"UPI • Bank • Wallet",line3:"Instant secure deposit",link:"/deposit"},
{icon:"🏦",title:"Withdraw",line1:"Request withdrawal",line2:"Bank transfer available",line3:"Fast settlement",link:"/withdraw"},
{icon:"📄",title:"Account Statement",line1:"Complete transaction report",line2:"Deposit and withdrawal details",line3:"Date wise statement",link:"/account-statement"},
{icon:"🎲",title:"Bet History",line1:"View all placed bets",line2:"Open and settled bets",line3:"Game wise history",link:"/bet-history"},
{icon:"⏳",title:"Unsettled Amount",line1:"Pending bet amount",line2:"Waiting for result",line3:"Live unsettled balance",link:"/unsettled-amount"},
{icon:"📊",title:"Profit & Loss",line1:"Daily profit loss report",line2:"Game wise P&L",line3:"Complete earning summary",link:"/profit-loss"},
{icon:"🎁",title:"Bonus Report",line1:"Bonus and cashback details",line2:"Offer reward history",line3:"Promotion benefits",link:"/bonus-report"},
{icon:"🏆",title:"Winning History",line1:"All winning records",line2:"Recent winning payout",line3:"Complete win report",link:"/winning-history"},
{icon:"🔔",title:"Notifications",line1:"Important account alerts",line2:"Game and wallet updates",line3:"Latest announcements",link:"/notifications"},
{icon:"🎧",title:"Customer Support",line1:"Need help with account",line2:"Deposit withdraw support",line3:"Contact support team",link:"/support"}
];

export default function UserMenu(){
  return(
    <div className="um-page">
      <header className="um-top">
        <button onClick={()=>window.history.back()} className="um-back">‹</button>
        <h2>MY ACCOUNT</h2>
        <span className="um-user">DEM123</span>
      </header>
      <section className="um-wallet">
        <div>
          <span>Wallet Balance</span>
          <b>₹0.00</b>
        </div>
        <button onClick={()=>window.location.href="/deposit"}>Deposit</button>
      </section>
      <main className="um-list">
        {userMenuItems.map((item,index)=>(
          <button className="um-card" key={index} onClick={()=>window.location.href=item.link}>
            <span className="um-icon">{item.icon}</span>
            <div className="um-text">
              <h3>{item.title}</h3>
              <p>{item.line1}</p>
              <p>{item.line2}</p>
              <p>{item.line3}</p>
            </div>
            <b className="um-arrow">›</b>
          </button>
        ))}
      </main>
    </div>
  );
}
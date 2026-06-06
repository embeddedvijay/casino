import React,{useState}from"react";
import{createPortal}from"react-dom";
import"./UserMenuLayout.css";

const menuItems=[
{icon:"💰",name:"Deposit",link:"/deposit"},
{icon:"🏦",name:"Withdraw",link:"/withdraw"},
{icon:"📄",name:"Account Statement",link:"/account-statement"},
{icon:"🎲",name:"Bet History",link:"/bet-history"},
{icon:"⏳",name:"Unsettled Amount",link:"/unsettled-amount"},
{icon:"📊",name:"Profit & Loss",link:"/profit-loss"},
{icon:"🎁",name:"Bonus Report",link:"/bonus-report"},
{icon:"🏆",name:"Winning History",link:"/winning-history"},
{icon:"🔔",name:"Notifications",link:"/notifications"},
{icon:"🎧",name:"Customer Support",link:"/support"}
];

export default function UserMenuLayout(){
const[open,setOpen]=useState(false);
const sidebar=open?(
<>
<div className="uml-overlay" onClick={()=>setOpen(false)}></div>
<div className="uml-sidebar">
<div className="uml-head">
<h3>MY ACCOUNT</h3>
<button onClick={()=>setOpen(false)}>✕</button>
</div>
{menuItems.map((item,index)=>(
<div className="uml-item" key={index} onClick={()=>window.location.href=item.link}>
<span>{item.icon}</span>
<b>{item.name}</b>
</div>
))}
</div>
</>
):null;
return(
<>
<button className="uml-menu-btn" onClick={()=>setOpen(true)}>☰</button>
{createPortal(sidebar,document.body)}
</>
);
}
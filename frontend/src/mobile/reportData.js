import{amountOf,money,portalRequest,statusOf,title,when}from"./portalApi.js";

const FINAL=new Set(["won","win","lost","lose","settled","completed","cashed_out","success","cancelled","refunded","void"]);
const OPEN=new Set(["active","pending","open","placed","accepted","unsettled","betting","processing"]);
const iso=date=>date.toISOString().slice(0,10);
export const defaultReportFilters=()=>({from:iso(new Date(Date.now()-6*86400000)),to:iso(new Date()),game:"all"});

export const rowDate=row=>row.created_at||row.CreatedAt||row.placed_at||row.timestamp||row.updated_at||row.SettledAt||null;
export const dateMatches=(row,from,to)=>{const raw=rowDate(row);if(!raw)return true;const value=new Date(raw).getTime();if(Number.isNaN(value))return true;const start=from?new Date(`${from}T00:00:00`).getTime():-Infinity;const end=to?new Date(`${to}T23:59:59.999`).getTime():Infinity;return value>=start&&value<=end};
export const payoutOf=row=>Number(row.payout??row.cashout_amount??row.win_amount??row.Win_Amt??0);
export const normalizeBet=row=>{const amount=Math.abs(amountOf(row)||Number(row.Total||0)),payout=Math.max(0,payoutOf(row));let status=statusOf(row);const settled=row.settled===true||row.Settled===true||Boolean(row.settled_at||row.SettledAt||row.resolved_at||row.completed_at);if((!status||status==="pending")&&settled)status=payout>0?"won":"lost";const isSettled=settled||FINAL.has(status),open=OPEN.has(status)||(!isSettled&&status!=="cancelled");const rawMarket=String(row.market||row.Market||"").trim(),isOpen=rawMarket.toUpperCase().endsWith("_OP"),isClose=rawMarket.toUpperCase().endsWith("_CL"),marketName=row.market_name||((isOpen||isClose)?rawMarket.slice(0,-3).replaceAll("_"," ").replace(/\b\w/g,char=>char.toUpperCase()):rawMarket.replaceAll("_"," ")),marketSide=row.market_side||(isOpen?"Open":isClose?"Close":""),market=marketName?(marketSide?`${marketName} • ${marketSide}`:marketName):"";return{raw:row,id:String(row.bet_id||row.transaction_id||row.round_id||row._id||"—"),game:title(row.game||row.game_type||row.collection||"Casino"),amount,payout,status,settled:isSettled,open,won:isSettled&&!open&&(status==="won"||status==="win"||payout>0),created:rowDate(row),market,marketName,marketSide,profit:Math.round((payout-amount)*100)/100}};
export const sum=(rows,key)=>rows.reduce((total,row)=>total+Number(row[key]||0),0);
export const signedMoney=value=>`${value<0?"-":"+"}${money(Math.abs(value))}`;
export const betListItem=row=>({id:row.id,title:row.game,detail:`Bet ${money(row.amount)} • Payout ${money(row.payout)}${row.market?` • ${row.market}`:""}`,meta:`${row.id} • ${when(row.created)}`,status:title(row.status),icon:row.game.split(" ").map(word=>word[0]).join("").slice(0,2),tone:row.won?"green":["lost","lose","cancelled"].includes(row.status)?"red":""});

async function loadPages(path,query={}){const items=[];for(let page=1;page<=20;page+=1){const data=await portalRequest(path,{query:{...query,page,limit:100}});items.push(...(data.items||[]));if(!data.has_more)break}return items}
export async function loadFilteredBets({game="all",from="",to=""}={}){const rows=await loadPages("/bets/history",{game});return rows.filter(row=>dateMatches(row,from,to)).map(normalizeBet)}
export async function loadFilteredTransactions({from="",to=""}={}){const rows=await loadPages("/wallet/transactions");return rows.filter(row=>dateMatches(row,from,to))}

export function dailyRows(rows){const groups=new Map();rows.forEach(row=>{const date=row.created?new Date(row.created):null,key=date&&!Number.isNaN(date.valueOf())?date.toLocaleDateString("en-CA"):"Unknown",current=groups.get(key)||{key,time:date?.valueOf()||0,amount:0,payout:0,profit:0};current.amount+=row.amount;current.payout+=row.payout;current.profit+=row.profit;groups.set(key,current)});return[...groups.values()].sort((a,b)=>b.time-a.time)}

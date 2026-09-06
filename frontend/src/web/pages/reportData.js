import{amountOf,money,payoutOf,portalRequest,statusOf,title,when}from"../../mobile/portalApi.js";

const FINAL_STATUSES=new Set(["won","win","lost","lose","settled","completed","cashed_out","success","cancelled","refunded","void"]);
const OPEN_STATUSES=new Set(["active","pending","open","placed","accepted","unsettled","betting","processing"]);

export async function loadAllBets(){
  const items=[];
  for(let page=1;page<=20;page+=1){
    const data=await portalRequest("/bets/history",{query:{page,limit:100}});
    items.push(...(data.items||[]));
    if(!data.has_more)break;
  }
  return items;
}

export function normalizedBet(row){
  const amount=Math.abs(amountOf(row));
  const payout=Math.max(0,payoutOf(row));
  let status=statusOf(row);
  const explicitlySettled=row.settled===true||Boolean(row.settled_at||row.resolved_at||row.completed_at);
  if((!status||status==="pending")&&explicitlySettled)status=payout>0?"won":"lost";
  const settled=explicitlySettled||FINAL_STATUSES.has(status);
  const open=OPEN_STATUSES.has(status)||(!settled&&status!=="cancelled");
  const won=settled&&!open&&(status==="won"||status==="win"||payout>0);
  const created=row.created_at||row.placed_at||row.timestamp||row.Time;
  const marketName=row.market_name||"";
  const marketSide=row.market_side||"";
  const market=row.market||(marketName?(marketSide?`${marketName} • ${marketSide}`:marketName):"");
  return{
    raw:row,
    id:String(row.bet_id||row.transaction_id||row.round_id||row._id||"—"),
    game:title(row.game||row.collection||row.game_type||"Casino"),
    amount,
    payout,
    status,
    settled,
    open,
    won,
    created,
    market,
    marketName,
    marketSide,
    dateLabel:when(created),
    profit:Math.round((payout-amount)*100)/100,
  };
}

export const sum=(rows,key)=>rows.reduce((total,row)=>total+Number(row[key]||0),0);
export const signedMoney=(value)=>`${value<0?"-":"+"}${money(Math.abs(value))}`;

export function dailyRows(rows){
  const groups=new Map();
  rows.forEach(row=>{
    const date=row.created?new Date(row.created):null;
    const key=date&&!Number.isNaN(date.valueOf())?date.toLocaleDateString("en-CA"):"Unknown";
    const current=groups.get(key)||{key,date:date?.valueOf()||0,amount:0,payout:0,profit:0};
    current.amount+=row.amount;current.payout+=row.payout;current.profit+=row.profit;groups.set(key,current);
  });
  return[...groups.values()].sort((a,b)=>b.date-a.date);
}

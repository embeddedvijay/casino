import React,{useEffect,useMemo,useState}from"react";
import"./MobileluckyRace.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;
const WS=`ws://${HOST}:8005/ws/lucky-race`;
const USER_ID="demo_user";
const LOGO="/new-logos/";

const fileName=(name)=>name==="land_rover"?"land_rover.png":`${name}.png`;

const logos=[
["bmw",22,10],
["ferrari",33,10],
["jaguar",44,10],
["star",53,10],
["lamborghini",62,10],
["land_rover",73,10],
["maserati",84,11],
["mercedes",92,17],
["porsche",94,30],

["bmw",94,44],
["ferrari",94,57],
["jaguar",92,69],
["lamborghini",85,77],
["land_rover",75,78],
["maserati",64,78],
["mercedes",54,78],
["porsche",44,78],

["bmw",34,78],
["ferrari",24,78],
["jaguar",14,76],
["lamborghini",6,66],
["land_rover",5,52],
["maserati",5,38],
["mercedes",5,24],
["porsche",11,13]
];

const betCars=[
"bmw",
"ferrari",
"jaguar",
"lamborghini",
"land_rover",
"maserati",
"mercedes",
"porsche"
];

const coins=[
50,
100,
200,
500,
1000
];

const money=(v)=>Number(v||0).toFixed(2);

const prettyName=(name="")=>String(name).replace("_"," ").toUpperCase();

function CarLogo({name,className=""}){
if(!name)return null;
return(
<img
className={className}
src={`${LOGO}${fileName(name)}`}
alt={name}
draggable="false"
/>
);
}

function RaceBoard({trackIndex,phase,winner,localBets,placeCoinBet}){
const safeIndex=Number(trackIndex||0)%logos.length;
const active=logos[safeIndex]||logos[0];

return(
<div className="mlr-board">
<div className="mlr-track-area">
{logos.map(([logo,x,y],i)=>(
<div
key={`${logo}-${i}`}
className={`mlr-track-logo ${i===safeIndex?"active":""}`}
style={{left:`${x}%`,top:`${y}%`}}
>
<CarLogo name={logo}/>
</div>
))}

<div
className={`mlr-moving-marker ${phase==="stopping"?"stop-effect":""}`}
style={{left:`${active[1]}%`,top:`${active[2]}%`}}
>
<CarLogo name={active[0]}/>
</div>
</div>

<div className="mlr-betting-grid">
{betCars.map((car)=>(
<button
className="mlr-bet-cell"
key={car}
onClick={()=>placeCoinBet(car)}
>
<CarLogo name={car} className="mlr-bet-logo"/>
<span>₹ {localBets[car]||"0"}</span>
</button>
))}
</div>

{phase==="result"&&winner&&(
<div className="mlr-winner-popup">
<b>WINNER</b>
<CarLogo name={winner.key}/>
</div>
)}
</div>
);
}

function TopBar({totalBet,totalWin,roundId,phase,countdown}){
return(
<header className="mlr-top">
<div className="mlr-brand">♛ GOLD365</div>

<div className="mlr-mini-stats">
<span>Bet ₹{money(totalBet)}</span>
<span>Win ₹{money(totalWin)}</span>
<span>{phase}</span>
<b>{String(countdown||0).padStart(2,"0")}</b>
</div>

<small>{roundId||"-"}</small>
</header>
);
}

function ResultStrip({history}){
return(
<section className="mlr-results">
<b>RESULT</b>

<div>
{history.length===0?(
<span className="mlr-empty">No Result</span>
):(
history.slice(-8).reverse().map((item)=>(
<span className="mlr-result-logo" key={item.round_id}>
<CarLogo name={item.winner?.key}/>
</span>
))
)}
</div>
</section>
);
}

function CoinPanel({selectedCoin,setSelectedCoin,clearBets}){
return(
<div className="mlr-coins">
{coins.map((coin)=>(
<button
key={coin}
className={selectedCoin===coin?"active":""}
onClick={()=>setSelectedCoin(coin)}
>
₹{coin}
</button>
))}

<button className="clear" onClick={clearBets}>
CLEAR
</button>
</div>
);
}

export default function MobileLuckyRace(){
const[gameState,setGameState]=useState(null);
const[selectedCoin,setSelectedCoin]=useState(10);
const[connection,setConnection]=useState("Connecting");
const[localBets,setLocalBets]=useState(Object.fromEntries(betCars.map((car)=>[car,"0"])));

useEffect(()=>{
const lockScreen=async()=>{
try{
if(window.screen?.orientation?.lock){
await window.screen.orientation.lock("portrait");
}
}catch(e){}
};

lockScreen();

return()=>{
try{
if(window.screen?.orientation?.unlock){
window.screen.orientation.unlock();
}
}catch(e){}
};
},[]);

const syncBets=(data)=>{
const next=Object.fromEntries(betCars.map((car)=>[car,"0"]));

if(data?.board_totals){
betCars.forEach((car)=>{
next[car]=String(data.board_totals?.[car]?.my||0);
});
}

setLocalBets(next);
};

useEffect(()=>{
fetch(`${API}/api/games/lucky-race/state`)
.then((res)=>res.json())
.then((data)=>{
setGameState(data);
syncBets(data);
})
.catch(()=>setConnection("Offline"));

const socket=new WebSocket(WS);

socket.onopen=()=>setConnection("Live connected");

socket.onmessage=(event)=>{
const msg=JSON.parse(event.data);

if(msg?.data){
setGameState(msg.data);
syncBets(msg.data);
}
};

socket.onerror=()=>setConnection("Connection error");
socket.onclose=()=>setConnection("Disconnected");

return()=>socket.close();
},[]);

const phase=gameState?.phase||"waiting";
const countdown=gameState?.countdown??0;
const trackIndex=(gameState?.track_index??0)%logos.length;
const history=gameState?.history||[];
const myBets=gameState?.my_bets||[];
const winner=gameState?.winner||null;

const totalBet=useMemo(()=>{
return Object.values(localBets).reduce((sum,value)=>sum+Number(value||0),0);
},[localBets]);

const totalWin=useMemo(()=>{
return myBets.reduce((sum,bet)=>sum+Number(bet.payout||0),0);
},[myBets]);

const placeCoinBet=async(car)=>{
if(phase!=="betting")return;

await fetch(`${API}/api/games/lucky-race/bet`,{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
user_id:USER_ID,
bet_type:car,
amount:selectedCoin
})
});
};

const clearBets=async()=>{
await fetch(`${API}/api/games/lucky-race/clear`,{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({user_id:USER_ID})
});
};

return(
<div className="mlr-page">
<TopBar
totalBet={totalBet}
totalWin={totalWin}
roundId={gameState?.round_id}
phase={phase}
countdown={countdown}
/>

<ResultStrip history={history}/>

<RaceBoard
trackIndex={trackIndex}
phase={phase}
winner={winner}
localBets={localBets}
placeCoinBet={placeCoinBet}
/>

<CoinPanel
selectedCoin={selectedCoin}
setSelectedCoin={setSelectedCoin}
clearBets={clearBets}
/>

{phase==="result"&&winner&&(
<div className="mlr-win">
<div className="mlr-win-card">
<h1>WINNER</h1>
<CarLogo name={winner.key}/>
<h2>{prettyName(winner.key)}</h2>
<p>YOU WIN ₹ {money(totalWin)}</p>
</div>
</div>
)}
</div>
);
}
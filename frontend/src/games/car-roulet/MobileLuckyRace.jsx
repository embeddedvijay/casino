import React,{useEffect,useMemo,useState}from"react";
import"./MobileluckyRace.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;
const WS=`ws://${HOST}:8005/ws/lucky-race`;
const USER_ID="demo_user";
const LOGO="/new-logos/";

const fileName=(name)=>name==="land_rover"?"land_rover.png":`${name}.png`;

const logos=[
["bmw",27,14],
["ferrari",36,14],
["jaguar",45,14],
["lamborghini",53,14],
["land_rover",62,14],
["maserati",70,14],
["mercedes",80,16],
["porsche",87,23],

["bmw",91,34],
["ferrari",91,47],
["jaguar",91,59],
["lamborghini",91,71],
["land_rover",87,82],
["maserati",80,89],
["mercedes",71,91],
["porsche",62,91],

["bmw",53,91],
["ferrari",44,91],
["jaguar",35,91],
["lamborghini",27,91],
["land_rover",18,89],
["maserati",12,82],
["mercedes",8,71],
["porsche",8,59],

["bmw",8,47],
["ferrari",8,35],
["jaguar",12,23],
["lamborghini",19,16]
];

const trackLogos=[
["bmw",27,14],
["ferrari",34,14],
["jaguar",41,14],
["lamborghini",48,14],
["land_rover",55,14],
["maserati",62,14],
["mercedes",70,14],
["porsche",78,16],

["bmw",86,23],
["ferrari",91,34],
["jaguar",91,47],
["lamborghini",91,59],
["land_rover",91,71],
["maserati",87,82],
["mercedes",80,89],
["porsche",71,91],

["bmw",62,91],
["ferrari",53,91],
["jaguar",44,91],
["lamborghini",35,91],
["land_rover",27,91],
["maserati",18,89],
["mercedes",12,82],
["porsche",8,71],

["bmw",8,59],
["ferrari",8,47],
["jaguar",8,35],
["lamborghini",12,23],
["land_rover",19,16],
["maserati",27,14],
["mercedes",36,14],
["porsche",45,14],

["bmw",53,14],
["ferrari",62,14],
["jaguar",70,14],
["lamborghini",80,16],
["land_rover",87,23]
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

function DashboardPanel({phase,countdown,waitingSeconds,roundId,totalBet,totalWin}){
const safeWaiting=Number(waitingSeconds||15);
const safeCount=Number(countdown||0);
const progress=phase==="betting"?Math.max(0,Math.min(100,((safeWaiting-safeCount)/safeWaiting)*100)):phase==="spinning"||phase==="stopping"||phase==="result"?100:0;
return(
<div className="mlr-dashboard-panel">
<div className="mlr-round-id">ROUND ID : {roundId||"-"}</div>
<div className="mlr-dash-main">
<div className="mlr-dash-box">
<small>BET</small>
<b>₹ {money(totalBet)}</b>
</div>
<div className="mlr-dash-divider"/>
<div className="mlr-dash-box right">
<small>WIN</small>
<b>₹ {money(totalWin)}</b>
</div>
</div>
<div className="mlr-progress-wrap">
<div className="mlr-progress-fill" style={{width:`${progress}%`}}/>
<div className="mlr-progress-car" style={{left:`${progress}%`}}>🏎️</div>
<div className="mlr-finish">🏁</div>
</div>
<div className="mlr-time-left">
<span>TIME LEFT</span>
<b>{phase==="betting"?safeCount:phase===""?"GO":phase===""?"STOP":"0"}</b>
<small>{phase==="betting"?"SEC":phase.toUpperCase()}</small>
</div>
</div>
);
}

function RaceBoard({trackIndex,phase,winner,localBets,placeCoinBet,waitingSeconds,countdown,roundId,totalBet,totalWin}){
const safeIndex=Number(trackIndex||0)%logos.length;
const active=logos[safeIndex]||logos[0];
return(
<div className="mlr-board">
<div className="mlr-center-dashboard">
<DashboardPanel
phase={phase}
countdown={countdown}
waitingSeconds={waitingSeconds}
roundId={roundId}
totalBet={totalBet}
totalWin={totalWin}
/>
</div>
<div className="mlr-track-area">
{logos.map(([logo,x,y],index)=>(
<div
key={`${logo}-${index}`}
className={`mlr-track-logo ${index===safeIndex?"active":""}`}
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

function TopBar(){
return(
<header className="mlr-header">
<div className="mlr-header-brand">
<span>♛</span>
<strong>GOLD365</strong>
</div>
<div className="mlr-user-pill">
<div className="mlr-user-avatar">👤</div>
<div>
<strong>DEMO USER</strong>
<small>₹ 5,245.00 ●</small>
</div>
</div>
</header>
);
}

function ResultStrip({history}){
return(
<section className="mlr-results">
<b>RESULT</b>
<div className="mlr-result-list">
{history.length===0?(
<span className="mlr-empty">No Result</span>
):(
history.slice(-8).reverse().map((item,index)=>(
<span className="mlr-result-logo" key={`${item.round_id}-${index}`}>
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
<button className="clear" onClick={clearBets}>CLEAR</button>
</div>

);
}

export default function MobileLuckyRace(){
const[gameState,setGameState]=useState(null);
const[selectedCoin,setSelectedCoin]=useState(50);
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
const waitingSeconds=gameState?.waiting_seconds||15;
const trackIndex=(gameState?.track_index??0)%trackLogos.length;
const history=gameState?.history||[];
const myBets=gameState?.my_bets||[];
const winner=gameState?.winner||null;

const totalBet=useMemo(()=>Object.values(localBets).reduce((sum,value)=>sum+Number(value||0),0),[localBets]);
const totalWin=useMemo(()=>myBets.reduce((sum,bet)=>sum+Number(bet.payout||0),0),[myBets]);

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
<TopBar/>
<ResultStrip history={history}/>
<RaceBoard
trackIndex={trackIndex}
phase={phase}
winner={winner}
localBets={localBets}
placeCoinBet={placeCoinBet}
waitingSeconds={waitingSeconds}
countdown={countdown}
roundId={gameState?.round_id}
totalBet={totalBet}
totalWin={totalWin}
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
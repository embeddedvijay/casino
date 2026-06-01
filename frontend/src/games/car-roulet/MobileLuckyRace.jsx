import React,{useEffect,useMemo,useState}from"react";
import"./MobileluckyRace.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;
const WS=`ws://${HOST}:8005/ws/lucky-race`;
const USER_ID="demo_user";
const LOGO="/new-logos/";

const fileName=(name)=>name==="land_rover"?"land_rover.png":`${name}.png`;

const logos=[
["bmw",22,7],
["ferrari",28,7],
["jaguar",34,7],
["lamborghini",40,7],
["land_rover",46,7],
["maserati",54,7],
["star",50,7],
["mercedes",60,7],
["porsche",66,7],
["bmw",72,7],
["ferrari",78,7],
["jaguar",84,9],
["lamborghini",90,15],
["land_rover",94,27],
["maserati",97,40],
["mercedes",97,55],
["porsche",95,70],
["bmw",91,83],
["ferrari",86,90],
["jaguar",80,92],
["lamborghini",74,93],
["land_rover",68,93],
["maserati",62,93],
["mercedes",56,93],
["porsche",50,93],
["bmw",44,93],
["ferrari",38,93],
["jaguar",32,93],
["lamborghini",26,93],
["land_rover",20,93],
["maserati",14,90],
["mercedes",9,83],
["porsche",5,70],
["bmw",3,55],
["ferrari",3,40],
["jaguar",6,27],
["lamborghini",10,15],
["land_rover",16,9]
];

const betCars=["bmw","ferrari","jaguar","lamborghini","land_rover","maserati","mercedes","porsche"];
const coins=[50,100,200,500,1000];

const money=(v)=>Number(v||0).toFixed(2);
const prettyName=(name="")=>String(name).replace("_"," ").toUpperCase();

const mobileTrack=logos.map((item,index)=>{
const total=logos.length;
const angle=(-Math.PI/2)+(index/total)*Math.PI*2;
const x=50+43*Math.cos(angle);
const y=52+40*Math.sin(angle);
return[item[0],Number(x.toFixed(2)),Number(y.toFixed(2))];
});

function CarLogo({name,className=""}){
if(!name)return null;
return <img className={className} src={`${LOGO}${fileName(name)}`} alt={name} draggable="false"/>;
}

function RaceBoard({trackIndex,phase,winner,localBets,placeCoinBet}){
const active=mobileTrack[Number(trackIndex||0)%mobileTrack.length]||mobileTrack[0];
return(
<div className="mlr-board">
<div className="mlr-track-area">
{mobileTrack.map(([logo,x,y],i)=>(
<div key={`${logo}-${i}`} className={`mlr-track-logo ${i===trackIndex?"active":""}`} style={{left:`${x}%`,top:`${y}%`}}>
<CarLogo name={logo}/>
</div>
))}
<div className={`mlr-moving-marker ${phase==="stopping"?"stop-effect":""}`} style={{left:`${active[1]}%`,top:`${active[2]}%`}}>
<CarLogo name={active[0]}/>
</div>
</div>

<div className="mlr-betting-grid">
{betCars.map(car=>(
<button className="mlr-bet-cell" key={car} onClick={()=>placeCoinBet(car)}>
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
<b>LAST RESULT</b>
<div>
{history.length===0?(
<span className="mlr-empty">No Result</span>
):history.slice(-8).reverse().map(item=>(
<span className="mlr-result-logo" key={item.round_id}>
<CarLogo name={item.winner?.key}/>
</span>
))}
</div>
</section>
);
}

function CoinPanel({selectedCoin,setSelectedCoin,clearBets}){
return(
<div className="mlr-coins">
{coins.map(c=>(
<button key={c} className={selectedCoin===c?"active":""} onClick={()=>setSelectedCoin(c)}>₹{c}</button>
))}
<button className="clear" onClick={clearBets}>CLEAR</button>
</div>
);
}

export default function MobileLuckyRace(){
const[gameState,setGameState]=useState(null);
const[selectedCoin,setSelectedCoin]=useState(50);
const[connection,setConnection]=useState("Connecting");
const[localBets,setLocalBets]=useState(Object.fromEntries(betCars.map(car=>[car,"0"])));

const syncBets=(data)=>{
const next=Object.fromEntries(betCars.map(car=>[car,"0"]));
if(data?.board_totals){
betCars.forEach(car=>{
next[car]=String(data.board_totals?.[car]?.my||0);
});
}
setLocalBets(next);
};

useEffect(()=>{
fetch(`${API}/api/games/lucky-race/state`).then(res=>res.json()).then(data=>{
setGameState(data);
syncBets(data);
}).catch(()=>setConnection("Offline"));

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
const trackIndex=(gameState?.track_index??0)%mobileTrack.length;
const history=gameState?.history||[];
const myBets=gameState?.my_bets||[];
const winner=gameState?.winner||null;

const totalBet=useMemo(()=>Object.values(localBets).reduce((s,v)=>s+Number(v||0),0),[localBets]);
const totalWin=useMemo(()=>myBets.reduce((s,b)=>s+Number(b.payout||0),0),[myBets]);

const placeCoinBet=async(car)=>{
if(phase!=="betting")return;
await fetch(`${API}/api/games/lucky-race/bet`,{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({user_id:USER_ID,bet_type:car,amount:selectedCoin})
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
<TopBar totalBet={totalBet} totalWin={totalWin} roundId={gameState?.round_id} phase={phase} countdown={countdown}/>
<ResultStrip history={history}/>
<RaceBoard trackIndex={trackIndex} phase={phase} winner={winner} localBets={localBets} placeCoinBet={placeCoinBet}/>
<CoinPanel selectedCoin={selectedCoin} setSelectedCoin={setSelectedCoin} clearBets={clearBets}/>

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
import React from "react";
import Aviator from "./games/aviator/Aviator.jsx";
import MobileAviator from "./games/aviator/MobileAviator.jsx";
import DragonTiger from "./games/dragon-tiger/DragonTiger.jsx";
import MobileDragonTiger from "./games/dragon-tiger/MobileDragonTiger.jsx";
import LuckyRace from "./games/car-roulet/LuckyRace.jsx";
import MobileLuckyRace from "./games/car-roulet/MobileLuckyRace.jsx";
import MatkaDashboard from "./games/matka/MatkaDashboard.jsx";
import MobileMatkaDashboard from "./games/matka/MobileMatkaDashboard.jsx";
import MarketInput from "./games/matka/MarketInput.jsx";
import MobileMarketInput from "./games/matka/MobileMarketInput.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import MobileLoginPage from "./pages/MobileLoginPage.jsx";
import CreateAccount from "./pages/CreateAccount.jsx";
import MobileCreateAccount from "./pages/MobileCreateAccount.jsx";
import ForgotPassword from "./pages/ForgotPassword.jsx";
import MobileForgotPassword from "./pages/MobileForgotPassword.jsx";
import MatkaInfo from "./games/matka/MatkaInfo.jsx";
import MobileMatkaInfo from "./games/matka/MobileMatkaInfo.jsx";

const lobbyGames=[
{path:"/aviator",tag:"HOT",theme:"#ff0b58",image:"/casino-assets/aviator.png",name:"AVIATOR"},
{path:"/dragon-tiger",tag:"POPULAR",theme:"#ffc400",image:"/casino-assets/dragon-tiger.png",name:"DRAGON TIGER"},
{path:"/lucky-race",tag:"NEW",theme:"#a855ff",image:"/casino-assets/lucky-race.png",name:"LUCKY RACE"},
{path:"/matka",tag:"CLASSIC",theme:"#b000ff",image:"/casino-assets/matka.png",name:"MATKA"},
];

function GameLobby(){
return(
<div style={styles.page}>
<style>{`@keyframes bgZoom{0%{transform:scale(1)}50%{transform:scale(1.06)}100%{transform:scale(1)}}@keyframes lightMove{0%{transform:translateX(-130%);opacity:0}35%{opacity:.45}100%{transform:translateX(130%);opacity:0}}@keyframes floatGlow{0%,100%{transform:translateY(0);opacity:.45}50%{transform:translateY(-18px);opacity:.85}}.casino-bg-anim{animation:bgZoom 18s ease-in-out infinite}.casino-light-sweep{animation:lightMove 7s linear infinite}.casino-float-glow{animation:floatGlow 4s ease-in-out infinite}`}</style>
<div style={styles.animatedBg} className="casino-bg-anim"/>
<div style={styles.overlay}/>
<div style={styles.lightSweep} className="casino-light-sweep"/>
<div style={styles.floatGlowOne} className="casino-float-glow"/>
<div style={styles.floatGlowTwo} className="casino-float-glow"/>
<header style={styles.header}><div style={styles.logoBox}><div style={styles.brand}><span style={styles.crown}>♛</span><strong>GOLD<span>365</span></strong></div><p style={styles.brandSub}>PLAY · WIN · REPEAT</p></div></header>
<section style={styles.cards}>{lobbyGames.map((game)=><a href={`/login?redirect=${encodeURIComponent(game.path)}`} key={game.path} style={{...styles.card,borderColor:game.theme,boxShadow:`0 0 26px ${game.theme}66`}}><div style={{...styles.ribbon,background:game.theme}}>{game.tag}</div><div style={{...styles.visual,backgroundImage:`url(${game.image})`}}/><button style={{...styles.playBtn,borderColor:game.theme,boxShadow:`0 0 18px ${game.theme}88`}}>PLAY NOW ›</button></a>)}</section>
<footer style={styles.footer}><div style={styles.footerItem}><span>🛡️</span><strong>100% SECURE</strong></div><div style={styles.footerItem}><span>🎧</span><strong>24/7 SUPPORT</strong></div><div style={styles.footerItem}><span>🏆</span><strong>FAIR PLAY</strong></div><div style={styles.footerItem}><span>🎁</span><strong>DAILY BONUS</strong></div></footer>
</div>
);
}

function MobileLobby(){
return(
<div style={mStyles.page}>
<style>{`@keyframes bgZoom{0%{transform:scale(1)}50%{transform:scale(1.05)}100%{transform:scale(1)}}@keyframes lightMove{0%{transform:translateX(-130%);opacity:0}35%{opacity:.35}100%{transform:translateX(130%);opacity:0}}@keyframes floatGlow{0%,100%{transform:translateY(0);opacity:.45}50%{transform:translateY(-14px);opacity:.8}}.casino-bg-anim{animation:bgZoom 18s ease-in-out infinite}.casino-light-sweep{animation:lightMove 7s linear infinite}.casino-float-glow{animation:floatGlow 4s ease-in-out infinite}`}</style>
<div style={mStyles.animatedBg} className="casino-bg-anim"/>
<div style={mStyles.overlay}/>
<div style={mStyles.lightSweep} className="casino-light-sweep"/>
<div style={mStyles.floatGlowOne} className="casino-float-glow"/>
<div style={mStyles.floatGlowTwo} className="casino-float-glow"/>
<header style={mStyles.header}>
  <div style={mStyles.logoBox}>
    <div style={mStyles.brand}><span style={mStyles.crown}>♛</span><strong>GOLD<span>365</span></strong></div>
    <p style={mStyles.brandSub}>PLAY · WIN · REPEAT</p>
  </div>
</header>
<section style={mStyles.cards}>
  {lobbyGames.map((game)=>
    <a href={`/login?redirect=${encodeURIComponent(game.path)}`} key={game.path} style={{...mStyles.card,borderColor:game.theme,boxShadow:`0 0 22px ${game.theme}66`}}>
      <div style={{...mStyles.ribbon,background:game.theme}}>{game.tag}</div>
      <div style={{...mStyles.visual,backgroundImage:`url(${game.image})`}}/>
      <button style={{...mStyles.playBtn,borderColor:game.theme,boxShadow:`0 0 14px ${game.theme}88`}}>PLAY NOW ›</button>
    </a>
  )}
</section>
<footer style={mStyles.footer}>
  <div style={mStyles.footerItem}><span>🛡️</span><strong>100% SECURE</strong></div>
  <div style={mStyles.footerItem}><span>🎧</span><strong>24/7 SUPPORT</strong></div>
  <div style={mStyles.footerItem}><span>🏆</span><strong>FAIR PLAY</strong></div>
  <div style={mStyles.footerItem}><span>🎁</span><strong>DAILY BONUS</strong></div>
</footer>
</div>
);
}

export default function App(){
const path=window.location.pathname;
const isMobile=window.innerWidth<=768;

if(path==="/aviator")return isMobile?<MobileAviator/>:<Aviator/>;
if(path==="/dragon-tiger")return isMobile?<MobileDragonTiger/>:<DragonTiger/>;
if(path==="/lucky-race")return isMobile?<MobileLuckyRace/>:<LuckyRace/>;
if(path==="/matka")return isMobile?<MobileMatkaDashboard/>:<MatkaDashboard/>;
if(path==="/login")return isMobile?<MobileLoginPage/>:<LoginPage/>;
if(path==="/create-account")return isMobile?<MobileCreateAccount/>:<CreateAccount/>;
if(path==="/forgot-password")return isMobile?<MobileForgotPassword/>:<ForgotPassword/>;
if(path==="/matka/info")return isMobile?<MobileMatkaInfo/>:<MatkaInfo/>;


if(path.startsWith("/matka/market-input/")){
const marketName=decodeURIComponent(path.split("/matka/market-input/")[1]||"");
window.history.replaceState({marketName},"","/matka/market-input");
return isMobile?<MobileMarketInput marketName={marketName}/>:<MarketInput marketName={marketName}/>;
}

if(path==="/matka/market-input"){
const marketName=window.history.state?.marketName||"";
return isMobile?<MobileMarketInput marketName={marketName}/>:<MarketInput marketName={marketName}/>;
}

return isMobile?<MobileLobby/>:<GameLobby/>;
}

const styles={
page:{minHeight:"100vh",position:"relative",overflowX:"hidden",overflowY:"auto",color:"#fff",fontFamily:"Arial,sans-serif",padding:"28px 36px 34px",background:"#050505"},
animatedBg:{position:"absolute",inset:"-35px",backgroundImage:"url('/casino-assets/casino-bg.png')",backgroundSize:"cover",backgroundPosition:"center top",backgroundRepeat:"no-repeat",zIndex:0},
overlay:{position:"absolute",inset:0,pointerEvents:"none",zIndex:1,background:"linear-gradient(180deg,rgba(0,0,0,.04) 0%,rgba(0,0,0,.14) 42%,rgba(0,0,0,.72) 100%)"},
lightSweep:{position:"absolute",top:0,bottom:0,left:0,width:"45%",background:"linear-gradient(90deg,transparent,rgba(255,214,92,.18),transparent)",zIndex:2,pointerEvents:"none"},
floatGlowOne:{position:"absolute",left:"8%",top:"20%",width:180,height:180,borderRadius:"50%",background:"rgba(255,196,0,.18)",filter:"blur(55px)",zIndex:1},
floatGlowTwo:{position:"absolute",right:"8%",top:"26%",width:210,height:210,borderRadius:"50%",background:"rgba(176,0,255,.18)",filter:"blur(60px)",zIndex:1},
header:{position:"relative",zIndex:5,display:"flex",justifyContent:"flex-end",alignItems:"center"},
logoBox:{textAlign:"right",background:"rgba(0,0,0,.38)",border:"1px solid rgba(255,214,92,.35)",borderRadius:18,padding:"10px 18px 8px",backdropFilter:"blur(7px)"},
brand:{display:"flex",alignItems:"center",justifyContent:"flex-end",gap:10,color:"#ffd65c",fontSize:36,fontWeight:1000,textShadow:"0 0 18px rgba(255,214,92,.65)",lineHeight:1},
crown:{fontSize:44},
brandSub:{margin:"6px 0 0",color:"#f7d36a",letterSpacing:4,fontWeight:700,fontSize:12},
cards:{position:"relative",zIndex:5,display:"grid",gridTemplateColumns:"repeat(4,minmax(0,1fr))",gap:24,marginTop:225},
card:{position:"relative",minHeight:500,border:"2px solid",borderRadius:24,overflow:"hidden",padding:18,textDecoration:"none",color:"#fff",background:"linear-gradient(180deg,rgba(255,255,255,.06),rgba(0,0,0,.48))",backdropFilter:"blur(4px)"},
ribbon:{position:"absolute",top:22,left:-42,transform:"rotate(-45deg)",width:165,textAlign:"center",padding:"8px 0",fontWeight:1000,fontSize:17,zIndex:3},
visual:{height:345,width:"100%",borderRadius:18,backgroundSize:"100% 100%",backgroundPosition:"center",backgroundRepeat:"no-repeat",boxShadow:"inset 0 -45px 70px rgba(0,0,0,.45)",marginBottom:14},
playBtn:{position:"absolute",left:32,right:32,bottom:26,height:62,borderRadius:18,border:"2px solid",background:"rgba(0,0,0,.50)",color:"#fff",fontSize:24,fontWeight:1000,cursor:"pointer"},
footer:{position:"relative",zIndex:5,maxWidth:1180,margin:"34px auto 0",minHeight:82,borderRadius:24,background:"rgba(0,0,0,.56)",border:"1px solid rgba(255,255,255,.16)",display:"grid",gridTemplateColumns:"repeat(4,1fr)",alignItems:"center",padding:"0 34px",backdropFilter:"blur(8px)"},
footerItem:{display:"flex",alignItems:"center",justifyContent:"center",gap:8,color:"#fff"}
};

const mStyles={
page:{minHeight:"100vh",position:"relative",overflowY:"auto",overflowX:"hidden",color:"#fff",fontFamily:"Arial,sans-serif",padding:"18px 12px 24px",background:"#050505"},
animatedBg:{position:"fixed",inset:"-24px",backgroundImage:"url('/casino-assets/casino-bg.png')",backgroundSize:"cover",backgroundPosition:"center top",backgroundRepeat:"no-repeat",zIndex:0},
overlay:{position:"fixed",inset:0,pointerEvents:"none",zIndex:1,background:"linear-gradient(180deg,rgba(0,0,0,.10) 0%,rgba(0,0,0,.35) 42%,rgba(0,0,0,.82) 100%)"},
lightSweep:{position:"fixed",top:0,bottom:0,left:0,width:"55%",background:"linear-gradient(90deg,transparent,rgba(255,214,92,.12),transparent)",zIndex:2,pointerEvents:"none"},
floatGlowOne:{position:"fixed",left:"8%",top:"18%",width:110,height:110,borderRadius:"50%",background:"rgba(255,196,0,.17)",filter:"blur(42px)",zIndex:1},
floatGlowTwo:{position:"fixed",right:"8%",top:"30%",width:130,height:130,borderRadius:"50%",background:"rgba(176,0,255,.17)",filter:"blur(45px)",zIndex:1},
header:{position:"relative",zIndex:5,display:"flex",justifyContent:"center",alignItems:"center",padding:"4px 0 10px"},
logoBox:{textAlign:"center",background:"rgba(0,0,0,.45)",border:"1px solid rgba(255,214,92,.35)",borderRadius:16,padding:"9px 16px 7px",backdropFilter:"blur(7px)"},
brand:{display:"flex",alignItems:"center",justifyContent:"center",gap:8,color:"#ffd65c",fontSize:28,fontWeight:1000,textShadow:"0 0 16px rgba(255,214,92,.7)",lineHeight:1},
crown:{fontSize:32},
brandSub:{margin:"5px 0 0",color:"#f7d36a",letterSpacing:3,fontWeight:700,fontSize:10},
cards:{position:"relative",zIndex:5,display:"grid",gridTemplateColumns:"1fr",gap:16,marginTop:10},
card:{position:"relative",minHeight:300,border:"2px solid",borderRadius:22,overflow:"hidden",padding:13,textDecoration:"none",color:"#fff",background:"linear-gradient(180deg,rgba(255,255,255,.06),rgba(0,0,0,.55))",backdropFilter:"blur(4px)"},
ribbon:{position:"absolute",top:18,left:-43,transform:"rotate(-45deg)",width:150,textAlign:"center",padding:"7px 0",fontWeight:1000,fontSize:13,zIndex:3},
visual:{height:200,width:"100%",borderRadius:17,backgroundSize:"100% 100%",backgroundPosition:"center",backgroundRepeat:"no-repeat",boxShadow:"inset 0 -45px 70px rgba(0,0,0,.48)",marginBottom:12},
playBtn:{position:"absolute",left:20,right:20,bottom:18,height:50,borderRadius:16,border:"2px solid",background:"rgba(0,0,0,.55)",color:"#fff",fontSize:18,fontWeight:1000,cursor:"pointer"},
footer:{position:"relative",zIndex:5,margin:"18px auto 0",minHeight:72,borderRadius:18,background:"rgba(0,0,0,.56)",border:"1px solid rgba(255,255,255,.16)",display:"grid",gridTemplateColumns:"repeat(2,1fr)",gap:8,alignItems:"center",padding:"12px",backdropFilter:"blur(8px)"},
footerItem:{display:"flex",alignItems:"center",justifyContent:"center",gap:6,color:"#fff",fontSize:12}
};
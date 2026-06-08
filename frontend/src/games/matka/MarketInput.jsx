import React,{useEffect,useState}from"react";
import"./matkaDashboardInput.css";
import UserMenuLayout from"../../shared/UserMenuLayout";
import{fetchCurrentUser}from"../../shared/userSession";

const API="http://localhost:8005";

export default function MatkaInput({marketName:marketFromApp=""}){
  const marketName=(marketFromApp||decodeURIComponent(window.location.pathname.split("/matka/market-input/")[1]||"")).toUpperCase();
  const[message,setMessage]=useState("");
  const[sentMessage,setSentMessage]=useState("");
  const[serverResponse,setServerResponse]=useState("");
  const[timeKey,setTimeKey]=useState("");
  const[loading,setLoading]=useState(false);
  const[confirming,setConfirming]=useState(false);
  const[confirmed,setConfirmed]=useState(false);
  const[user,setUser]=useState({user_name:"DEMO123",balance:0});

  useEffect(()=>{
    fetchCurrentUser().then((data)=>setUser(data||{user_name:"DEMO123",balance:0})).catch(()=>setUser({user_name:"DEMO123",balance:0}));
  },[]);

  const getUserId=()=>user?.user_id||user?.id||user?._id||user?.user_name||localStorage.getItem("user_id")||"guest";

  const formatResult=(rows,total)=>{
    if(!Array.isArray(rows)||!rows.length)return"";
    const lines=rows.map(row=>{
      if(!Array.isArray(row))return String(row);
      const nums=row.slice(0,-1).join(", ");
      const amount=row[row.length-1];
      return `${nums} = ${amount}`;
    }).join("\n");
    return `${lines}\n\nTOTAL = ${total}`;
  };

  const autoGrow=e=>{
    setMessage(e.target.value);
    e.target.style.height="auto";
    e.target.style.height=e.target.scrollHeight+"px";
  };

  const sendMessage=async()=>{
    if(!message.trim()){
      alert("Message type karo");
      return;
    }
    if(!marketName){
      alert("Market name nahi mila");
      return;
    }
    const cleanMessage=message.trim();
    setLoading(true);
    setServerResponse("");
    setConfirmed(false);
    setSentMessage("");
    setTimeKey("");
    try{
      const res=await fetch(`${API}/api/games/matka/market-message`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          client_id:"demo",
          user_id:getUserId(),
          market_name:marketName,
          market:marketName,
          time_key:marketName,
          message:cleanMessage
        })
      });
      const data=await res.json();
      if(data.success){
        const nextTimeKey=data.time_key||marketName;
        setTimeKey(nextTimeKey);
        setSentMessage(cleanMessage);
        setMessage("");
        const resultText=formatResult(data.result,data.total);
        setServerResponse(`${data.market_name||marketName}\n${nextTimeKey?`\n${nextTimeKey}`:""}\n\n${resultText}\n\nConfirm karna hai?`);
      }else{
        setServerResponse(data.reply||data.message||data.response||data.table_type||JSON.stringify(data,null,2)||"Invalid format");
      }
    }catch(e){
      setServerResponse("Backend error");
    }
    setLoading(false);
  };

  const confirmMessage=async()=>{
    if(!serverResponse){
      alert("Pehle send karo");
      return;
    }
    if(!sentMessage){
      alert("Pehle message send karo");
      return;
    }
    setConfirming(true);
    try{
      const res=await fetch(`${API}/api/games/matka/market-message/confirm`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          client_id:"demo",
          user_id:getUserId(),
          market_name:marketName,
          market:marketName,
          time_key:timeKey||marketName,
          message:sentMessage,
          server_response:serverResponse
        })
      });
      const data=await res.json();
      if(data.success){
        setConfirmed(true);
        setServerResponse(`✅ BET CONFIRMED\n\nMarket : ${marketName}\nTime Key : ${data.time_key||timeKey||marketName}\nTotal : ${data.total||0}\n\n${data.message||"Market message confirmed successfully"}`);
      }else{
        alert(data.message||data.reply||"Confirm failed");
      }
    }catch(e){
      alert("Confirm error");
    }
    setConfirming(false);
  };

  return(
    <div className="mi-page">
      <header className="mi-top">
        <div className="mi-brand">
          <span className="mi-home">⌂</span>
          <span>GOLD</span>
          <b>365</b>
        </div>
        <div className="mi-profile">
          <span>🌐</span>
          <span className="balance">{Number(user?.balance||0).toFixed(2)}</span>
          <UserMenuLayout/>
          <span className="user">{user?.user_name||"DEMO123"}</span>
        </div>
      </header>

      <div className="mi-header">
        <h1>MATKA</h1>
        <h2>MARKET MESSAGE</h2>
        <p>Send Game for this market.</p>
      </div>

      <div className="mi-card">
        <h3>MARKET MESSAGE INPUT</h3>
        <label>Market Name</label>
        <input value={marketName} readOnly/>
        <label>Message</label>
        <textarea value={message} onChange={autoGrow} onKeyDown={(e)=>{if(e.key==="Enter"&&e.ctrlKey){e.preventDefault();sendMessage();}}} maxLength={500} placeholder="Type your game message..." rows={1}/>
        <div className="mi-count">{message.length} / 500</div>
        {sentMessage&&<div className="mi-sent-preview"><b>Last Sent:</b><pre>{sentMessage}</pre></div>}
        <button className="mi-send" onClick={sendMessage} disabled={loading}>{loading?"SENDING...":"SEND"}</button>
      </div>

      <div className="mi-card">
        <h3>SERVER RESPONSE</h3>
        <div className={confirmed?"mi-server-response success":"mi-server-response"}>{serverResponse||"No response yet"}</div>
      </div>

      <button className="mi-confirm" onClick={confirmMessage} disabled={confirming||!serverResponse||!sentMessage||confirmed}>{confirming?"CONFIRMING...":confirmed?"CONFIRMED":"CONFIRM"}</button>
    </div>
  );
}
import React,{useEffect,useState}from"react";
import"./matkaDashboardInput.css";
import UserMenuLayout from "../../shared/UserMenuLayout";
import{fetchCurrentUser}from"../../shared/userSession";

const API="http://localhost:8005";

export default function MatkaInput({marketName:marketFromApp=""}){
  const marketName=(marketFromApp||decodeURIComponent(window.location.pathname.split("/matka/market-input/")[1]||"")).toUpperCase();
  const[message,setMessage]=useState("");
  const[serverResponse,setServerResponse]=useState("");
  const[loading,setLoading]=useState(false);
  const[confirming,setConfirming]=useState(false);
  const[user,setUser]=useState({user_name:"DEMO123",balance:0});

  useEffect(()=>{
    fetchCurrentUser().then(setUser);
  },[]);
  const sendMessage=async()=>{
    if(!message.trim()){
      alert("Message type karo");
      return;
    }
    if(!marketName){
      alert("Market name nahi mila");
      return;
    }
    setLoading(true);
    setServerResponse("");
    try{
      const res=await fetch(`${API}/api/games/matka/market-message`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({market:marketName,message:message.trim()})
      });
      const data=await res.json();
      setServerResponse(data.message||data.response||data.table_type||JSON.stringify(data,null,2));
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
    setConfirming(true);
    try{
      const res=await fetch(`${API}/api/games/matka/market-message/confirm`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({market:marketName,message:message.trim(),server_response:serverResponse})
      });
      const data=await res.json();
      alert(data.message||"Confirmed");
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
        <p>Send Game for this market. </p>
      </div>

      <div className="mi-card">
        <h3>MARKET MESSAGE INPUT</h3>
        <label>Market Name</label>
        <input value={marketName} readOnly/>
        <label>Message</label>
        <textarea value={message} onChange={(e)=>setMessage(e.target.value)} maxLength={160}/>
        <div className="mi-count">{message.length} / 160</div>
        <button className="mi-send" onClick={sendMessage} disabled={loading}>{loading?"SENDING...":"SEND"}</button>
      </div>

      <div className="mi-card">
        <h3>SERVER RESPONSE</h3>
        <div className="mi-server-response">{serverResponse}</div>
      </div>

      <button className="mi-confirm" onClick={confirmMessage} disabled={confirming}>{confirming?"CONFIRMING...":"CONFIRM"}</button>
    </div>
  );
}
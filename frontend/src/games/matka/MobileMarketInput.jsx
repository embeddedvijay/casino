import React,{useState}from"react";
import"./MobilematkaDashboardInput.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;

const nowTime=()=>new Date().toLocaleTimeString([],{
  hour:"2-digit",
  minute:"2-digit"
});

export default function MatkaInput({marketName:marketFromApp=""}){
  const marketName=(marketFromApp||decodeURIComponent(window.location.pathname.split("/matka/market-input/")[1]||"")).toUpperCase();

  const[message,setMessage]=useState("");
  const[sentMessage,setSentMessage]=useState("");
  const[serverResponse,setServerResponse]=useState("");
  const[loading,setLoading]=useState(false);
  const[confirming,setConfirming]=useState(false);
  const[confirmed,setConfirmed]=useState(false);
  const[msgTime,setMsgTime]=useState("");
  const[responseTime,setResponseTime]=useState("");
  const[confirmTime,setConfirmTime]=useState("");

  const goBack=()=>{
    window.history.back();
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
    setSentMessage(cleanMessage);
    setMsgTime(nowTime());

    try{
      const res=await fetch(`${API}/api/games/matka/market-message`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          market:marketName,
          message:cleanMessage
        })
      });

      const data=await res.json();

      setServerResponse(data.message||data.response||data.table_type||JSON.stringify(data,null,2));
      setResponseTime(nowTime());
    }catch(e){
      setServerResponse("Backend error");
      setResponseTime(nowTime());
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
        body:JSON.stringify({
          market:marketName,
          message:sentMessage||message.trim(),
          server_response:serverResponse
        })
      });

      const data=await res.json();

      setConfirmed(true);
      setConfirmTime(nowTime());
    }catch(e){
      alert("Confirm error");
    }

    setConfirming(false);
  };

  return(
    <div className="mci-chat-page">
      <header className="mci-chat-top">
        <button className="mci-chat-back" onClick={goBack}>‹</button>

        <div className="mci-chat-logo">
          <span>♛</span>
        </div>

        <div className="mci-chat-title">
          <h3>{marketName||"MARKET"}</h3>
          <p>Market Message</p>
        </div>

        <div className="mci-secure">
          <span>🛡</span>
          <b>Secure</b>
        </div>
      </header>

      <main className="mci-chat-body">
        <div className="mci-date-pill">
          Today
        </div>

        <div className="mci-msg-row bot">
          <div className="mci-bot-icon">🤖</div>
          <div className="mci-bubble bot">
            <p>Welcome to <b>{marketName?.split("_").join(" ")}</b> market.</p>
            <p>Type your Game message below and send. </p>
            <small>{nowTime()}</small>
          </div>
        </div>

        {sentMessage&&(
          <div className="mci-msg-row user">
            <div className="mci-bubble user">
              <p>{sentMessage}</p>
              <small>{msgTime} ✓✓</small>
            </div>
          </div>
        )}

        {serverResponse&&(
          <div className="mci-msg-row bot">
            <div className="mci-bot-icon">🤖</div>
            <div className="mci-bubble bot response">
              <h4>{marketName} RESPONSE</h4>
              <pre>{serverResponse}</pre>
              <small>{responseTime}</small>
            </div>
          </div>
        )}

        {serverResponse&&!confirmed&&(
          <button className="mci-confirm-message" onClick={confirmMessage} disabled={confirming}>
            <span>🛡</span>
            {confirming?"CONFIRMING...":"CONFIRM MESSAGE"}
          </button>
        )}

        {confirmed&&(
          <>
            <div className="mci-msg-row user">
              <div className="mci-bubble user">
                <p>Confirm</p>
                <small>{confirmTime} ✓✓</small>
              </div>
            </div>

            <div className="mci-msg-row bot">
              <div className="mci-bot-icon">🤖</div>
              <div className="mci-bubble bot">
                <p>✅ Market message confirmed successfully.</p>
                <small>{confirmTime}</small>
              </div>
            </div>
          </>
        )}
      </main>

      <footer className="mci-chat-input">
        <div className="mci-input-box">
          <span>☺</span>
          <textarea
            value={message}
            onChange={(e)=>setMessage(e.target.value)}
            maxLength={160}
            placeholder="Type your market message..."
            rows={1}
          />
        </div>

        <button className="mci-send-btn" onClick={sendMessage} disabled={loading}>
          {loading?"...":"➤"}
        </button>
      </footer>

      <div className="mci-encrypt-note">
        <span>🔒</span>
        <div>
          <b>Your messages are secure</b>
          <p>We do not share your data with any third party.</p>
        </div>
      </div>
    </div>
  );
}
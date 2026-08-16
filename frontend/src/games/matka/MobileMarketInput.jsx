import React,{useEffect,useRef,useState}from"react";
import"./MobilematkaDashboardInput.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;

const getValue=(market,keys)=>{
  if(!market||typeof market!=="object")return"";
  for(const key of keys){
    if(market[key]!==undefined&&market[key]!==null&&String(market[key]).trim()!=="")return String(market[key]).trim();
  }
  return"";
};

const hasResult=(value)=>value!==""&&value!=="*"&&value!=="**"&&value!=="-"&&value!=="--";

const playLabel=(key,marketName)=>`${String(marketName||"").replaceAll("_"," ")} ${String(key||"").endsWith("_CL")?"CLOSE":"OPEN"}`;

const getMarketResult=(data,marketName)=>{
  const results=data?.Result&&typeof data.Result==="object"?data.Result:data||{};
  const keys=[marketName,`${marketName}_OP`,marketName.replace("_DAY",""),marketName.replace("_NIGHT","")];
  for(const key of keys){
    if(results[key])return results[key];
  }
  return null;
};

const resolvePlayTimeKey=async(marketName)=>{
  let configured=false;
  try{
    const configRes=await fetch(`${API}/api/games/matka/markets`);
    if(!configRes.ok)return marketName;
    const configData=await configRes.json();
    const markets=Array.isArray(configData)?configData:Array.isArray(configData?.markets)?configData.markets:[];
    const config=markets.find((item)=>String(item.key||"").toUpperCase()===marketName);
    if(!config?.open_time||!/^(\d{1,2}):(\d{2})$/.test(config.open_time))return marketName;
    configured=true;

    const[,hour,minute]=config.open_time.match(/^(\d{1,2}):(\d{2})$/);
    const now=new Date();
    const currentMinutes=now.getHours()*60+now.getMinutes();
    const openMinutes=Number(hour)*60+Number(minute);
    if(currentMinutes<openMinutes)return`${marketName}_OP`;

    const resultRes=await fetch(`${API}/api/games/matka/results/latest`,{cache:"no-store"});
    if(!resultRes.ok)return null;
    const market=getMarketResult(await resultRes.json(),marketName);
    const open=getValue(market,["OPEN","open"]);
    return hasResult(open)?`${marketName}_CL`:null;
  }catch(e){
    return configured?null:marketName;
  }
};

const nowTime=()=>new Date().toLocaleTimeString([],{
  hour:"2-digit",
  minute:"2-digit"
});

export default function MatkaInput({marketName:marketFromApp=""}){
  const marketName=(marketFromApp||decodeURIComponent(window.location.pathname.split("/matka/market-input/")[1]||"")).toUpperCase();

  const[message,setMessage]=useState("");
  const[sentMessage,setSentMessage]=useState("");
  const[serverResponse,setServerResponse]=useState("");
  const[timeKey,setTimeKey]=useState("");
  const[loading,setLoading]=useState(false);
  const[confirming,setConfirming]=useState(false);
  const[confirmed,setConfirmed]=useState(false);
  const[confirmedMessage,setConfirmedMessage]=useState("");
  const[msgTime,setMsgTime]=useState("");
  const[responseTime,setResponseTime]=useState("");
  const[confirmTime,setConfirmTime]=useState("");
  const bodyRef=useRef(null);
  const textareaRef=useRef(null);

  useEffect(()=>{
    if(bodyRef.current){
      bodyRef.current.scrollTop=bodyRef.current.scrollHeight;
    }
  },[sentMessage,serverResponse,confirmed,loading]);

  const goBack=()=>{
    window.history.back();
  };

  const resizeTextarea=el=>{
    if(!el)return;
    el.style.height="auto";
    el.style.height=Math.min(el.scrollHeight,150)+"px";
  };

  const changeMessage=e=>{
    setMessage(e.target.value);
    resizeTextarea(e.target);
  };

  const clearInput=()=>{
    setMessage("");
    if(textareaRef.current){
      textareaRef.current.style.height="42px";
    }
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

    const nextTimeKey=await resolvePlayTimeKey(marketName);
    if(!nextTimeKey){
      setSentMessage(cleanMessage);
      setServerResponse("Wait for open result");
      setMsgTime(nowTime());
      setResponseTime(nowTime());
      setConfirmed(false);
      return;
    }

    setLoading(true);
    setServerResponse("");
    setConfirmed(false);
    setSentMessage(cleanMessage);
    setMsgTime(nowTime());
    setTimeKey(nextTimeKey);
    clearInput();

    try{
      const res=await fetch(`${API}/api/games/matka/market-message`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          client_id:"demo",
          user_id:localStorage.getItem("user_id")||"guest",
          market_name:marketName,
          time_key:nextTimeKey,
          message:cleanMessage
        })
      });

      const data=await res.json();

      if(data.success){
        const resultText=Array.isArray(data.result)
          ? data.result.map(row=>{
              const nums=row.slice(0,-1).join(", ");
              const amount=row[row.length-1];
              return `${nums} = ${amount}`;
            }).join("\n")
          : "";

        setServerResponse(`${playLabel(data.time_key||nextTimeKey,marketName)}\n\n${resultText}\n\nTOTAL = ${data.total}\n\nConfirm karna hai?`);
      }else{
        setServerResponse(data.reply||data.message||"Invalid game format");
      }

      setResponseTime(nowTime());
    }catch(e){
      setServerResponse("Backend error");
      setResponseTime(nowTime());
    }

    setLoading(false);
  };

  const confirmMessage=async()=>{
    if(serverResponse==="Wait for open result")return;
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
          client_id:"demo",
          user_id:localStorage.getItem("user_id")||"guest",
          market_name:marketName,
          market:marketName,
          time_key:timeKey||marketName,
          message:sentMessage,
          server_response:serverResponse
        })
      });

      const data=await res.json();

      if(data.success!==false){
        const confirmedKey=data.time_key||timeKey||marketName;
        setConfirmedMessage(`✅ GAME CONFIRMED\n\n${playLabel(confirmedKey,marketName)}\n\nConfirmed Message:\n${sentMessage}\n\nTOTAL = ${data.total??"-"}`);
        setConfirmed(true);
        setConfirmTime(nowTime());
      }else{
        alert(data.message||data.reply||"Confirm failed");
      }
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

      <main className="mci-chat-body" ref={bodyRef}>
        <div className="mci-date-pill">
          Today
        </div>

        <div className="mci-msg-row bot">
          <div className="mci-bot-icon">🤖</div>
          <div className="mci-bubble bot">
            <p>Welcome to <b>{marketName?.split("_").join(" ")}</b> market.</p>
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

        {loading&&(
          <div className="mci-msg-row bot">
            <div className="mci-bot-icon">🤖</div>
            <div className="mci-bubble bot">
              <p>Checking...</p>
              <small>{nowTime()}</small>
            </div>
          </div>
        )}

        {serverResponse&&(
          <div className="mci-msg-row bot">
            <div className="mci-bot-icon">🤖</div>
            <div className="mci-bubble bot response">
              <h4>{playLabel(timeKey,marketName)} RESPONSE</h4>
              <pre>{serverResponse}</pre>
              <small>{responseTime}</small>
            </div>
          </div>
        )}

        {serverResponse!=="Wait for open result"&&serverResponse&&!confirmed&&(
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
                <pre>{confirmedMessage}</pre>
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
            ref={textareaRef}
            value={message}
            onChange={changeMessage}
            onKeyDown={(e)=>{
              if(e.key==="Enter"&&e.ctrlKey){
                e.preventDefault();
                sendMessage();
              }
            }}
            maxLength={500}
            placeholder="Pls send your game..."
            rows={1}
          />
        </div>

        <button className="mci-send-btn" onClick={sendMessage} disabled={loading}>
          {loading?"...":"➤"}
        </button>
      </footer>


    </div>
  );
}
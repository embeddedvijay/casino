import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./Mobileaviator.css";
import UserMenuLayout from "../../shared/UserMenuLayout";
import{fetchCurrentUser}from"../../shared/userSession";


// const API = "http://localhost:8005";
// const WS = "ws://localhost:8005/ws/game";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;
const WS=`ws://${HOST}:8005/ws/game`;

function formatMoney(n) {
  return Number(n || 0).toFixed(2);
}

function historyClass(v) {
  if (v >= 10) return "pill pink";
  if (v >= 2) return "pill purple";
  return "pill blue";
}

function Plane({ phase, multiplier }) {
  const isBetting = phase === "betting";
  const isFlying = phase === "flying";
  const crashed = phase === "crashed";

  const safeMultiplier = Number(multiplier || 1);

  let planeLeft = 8;
  let planeBottom = 8;

  if (isFlying) {
    planeLeft = Math.min(8 + safeMultiplier * 9.5, 74);
    planeBottom = Math.min(8 + safeMultiplier * 4.2, 60);
  }

  if (crashed) {
    // Flew away / crash ke time plane box ke bahar chala jayega
    planeLeft = 110;
    planeBottom = 72;
  }

  const planeX = (planeLeft / 100) * 1000;
  const planeY = 420 - (planeBottom / 100) * 420;

  const lineStartX = 35;
  const lineStartY = 360;

  const lineEndX = Math.max(90, planeX + 35);
  const lineEndY = Math.min(365, planeY + 45);

  const controlOneX = lineStartX + (lineEndX - lineStartX) * 0.38;
  const controlOneY = lineStartY;

  const controlTwoX = lineStartX + (lineEndX - lineStartX) * 0.72;
  const controlTwoY = lineEndY + 25;

  return (
    <>
      {isFlying && (
        <svg
          className="flight-line-svg"
          viewBox="0 0 1000 420"
          preserveAspectRatio="none"
        >
          <path
            className="flight-line"
            d={`M ${lineStartX} ${lineStartY} C ${controlOneX} ${controlOneY}, ${controlTwoX} ${controlTwoY}, ${lineEndX} ${lineEndY}`}
          />
        </svg>
      )}

      <div
        className={`plane-wrap ${isBetting ? "idle return-home" : ""} ${
          isFlying ? "flying" : ""
        } ${crashed ? "flew-away" : ""}`}
        style={{
          left: `${planeLeft}%`,
          bottom: `${planeBottom}%`,
        }}
      >
        <svg
          className={`aviator-plane ${crashed ? "crash" : ""}`}
          viewBox="0 0 520 210"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="planeRedMain" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ff004f" />
              <stop offset="45%" stopColor="#f00048" />
              <stop offset="100%" stopColor="#af002f" />
            </linearGradient>

            <filter id="planeGlowRed" x="-40%" y="-40%" width="180%" height="180%">
              <feGaussianBlur stdDeviation="3.5" result="blur" />
              <feColorMatrix
                in="blur"
                type="matrix"
                values="1 0 0 0 1
                        0 0 0 0 0
                        0 0 0 0 0.25
                        0 0 0 0.9 0"
                result="glow"
              />
              <feMerge>
                <feMergeNode in="glow" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <g filter="url(#planeGlowRed)">
            <path
              className="flame flame-a"
              d="M52 136 C18 134 6 126 0 118 C31 121 58 122 91 124 Z"
            />
            <path
              className="flame flame-b"
              d="M70 154 C30 156 9 148 0 139 C39 137 69 137 112 139 Z"
            />

            <path
              className="plane-body"
              d="M35 126
                 C98 123 151 118 205 109
                 L327 73
                 C357 65 388 61 421 63
                 L485 65
                 C507 66 520 75 519 86
                 C518 97 505 104 481 108
                 L354 130
                 C286 142 224 149 155 150
                 L60 151
                 C39 151 28 145 27 137
                 C26 131 29 127 35 126 Z"
            />

            <path
              className="plane-nose"
              d="M421 63 L490 65 C510 67 520 75 519 86 C517 96 506 102 482 107 L431 116 C454 94 453 76 421 63 Z"
            />

            <path
              className="wing-main wing-animate"
              d="M214 113
                 L151 35
                 C146 29 149 23 157 24
                 L214 30
                 C224 31 230 36 236 44
                 L308 101 Z"
            />

            <path
              className="wing-dark wing-animate"
              d="M215 114 L169 52 L216 59 L282 103 Z"
            />

            <path
              className="tail-top tail-animate"
              d="M94 124
                 L45 62
                 C40 55 43 50 52 51
                 L89 54
                 C98 55 104 60 109 67
                 L164 119 Z"
            />

            <path
              className="tail-bottom tail-animate"
              d="M237 146
                 L174 199
                 C167 205 159 203 155 196
                 L143 173
                 L202 145 Z"
            />

            <path className="rear-fin" d="M72 147 L34 181 L99 150 Z" />

            <path className="window-line" d="M278 87 C316 78 358 74 405 76" />
            <circle className="window" cx="363" cy="82" r="8" />
            <circle className="window" cx="396" cy="79" r="7" />

            <path className="cut-line" d="M126 128 C198 125 265 111 333 87" />
            <path className="bottom-line" d="M59 145 C142 147 249 141 355 125" />

            <text className="plane-x" x="330" y="114" transform="rotate(-8 330 114)">
              X
            </text>
          </g>
        </svg>

        <div className="plane-smoke smoke-one" />
        <div className="plane-smoke smoke-two" />
        <div className="plane-smoke smoke-three" />
      </div>
    </>
  );
}

function BetPanel({ seat, phase, multiplier, roundId, myBets, onNotice }) {
  const [amount, setAmount] = useState(50);
  const [auto, setAuto] = useState(false);

  const activeBet = myBets.find((b) => b.seat === seat && b.round_id === roundId);
  const canBet = phase === "betting" && !activeBet;
  const canCashout = phase === "flying" && activeBet?.status === "active";

  async function placeBet() {
    try {
      const res = await fetch(`${API}/api/games/aviator/bet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "demo_user",
          seat,
          amount: Number(amount),
        }),
      });

      const data = await res.json();
      onNotice(data.message || "Done");
    } catch {
      onNotice("Backend not connected");
    }
  }

  async function cashout() {
    try {
      const res = await fetch(`${API}/api/games/aviator/cashout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "demo_user",
          seat,
        }),
      });

      const data = await res.json();
      onNotice(data.message || "Done");
    } catch {
      onNotice("Backend not connected");
    }
  }

  return (
    <div className="bet-panel">
      <div className="tab-switch">
        <button className={!auto ? "active" : ""} onClick={() => setAuto(false)}>
          Bet
        </button>
        <button className={auto ? "active" : ""} onClick={() => setAuto(true)}>
          Auto
        </button>
      </div>

      <div className="bet-body">
        <div className="amount-box">
          <div className="amount-input">
            <button onClick={() => setAmount(Math.max(10, Number(amount || 0) - 10))}>
              −
            </button>
            <input value={amount} onChange={(e) => setAmount(e.target.value)} />
            <button onClick={() => setAmount(Number(amount || 0) + 10)}>+</button>
          </div>

          <div className="quick">
            <button onClick={() => setAmount(10)}>10</button>
            <button onClick={() => setAmount(20)}>20</button>
            <button onClick={() => setAmount(50)}>50</button>
            <button onClick={() => setAmount(100)}>100</button>
          </div>
        </div>

        {canCashout ? (
          <button className="bet-btn orange" onClick={cashout}>
            CASH OUT
            <br />
            <span>{formatMoney(Number(activeBet.amount) * multiplier)} INR</span>
          </button>
        ) : (
          <button className="bet-btn" disabled={!canBet} onClick={placeBet}>
            BET
            <br />
            <span>{formatMoney(amount)} INR</span>
          </button>
        )}
      </div>

      {activeBet && (
        <div className={`bet-status ${activeBet.status}`}>
          {activeBet.status === "cashed_out"
            ? `Cashed out ${activeBet.cashout_multiplier}x = ${formatMoney(
                activeBet.cashout_amount
              )}`
            : activeBet.status === "lost"
            ? "Lost"
            : "Bet accepted"}
        </div>
      )}
    </div>
  );
}

function App() {
  const [data, setData] = useState({
    phase: "waiting",
    multiplier: 1,
    countdown: 0,
    waiting_seconds: 30,
    round_id: "",
    history: [],
    all_bets: [],
    my_bets: [],
  });

  const [notice, setNotice] = useState("");
  const [showHistory,setShowHistory]=useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    let retry;

    function connect() {
      const ws = new WebSocket(WS);

      ws.onopen = () => {
        setNotice("Live connected");
      };

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        if (msg.data) {
          setData(msg.data);
        }
      };

      ws.onclose = () => {
        setNotice("Reconnecting...");
        retry = setTimeout(connect, 1500);
      };

      ws.onerror = () => {
        setNotice("Socket error");
      };

      wsRef.current = ws;
    }

    connect();

    return () => {
      clearTimeout(retry);
      wsRef.current?.close();
    };
  }, []);

  const totalBet = useMemo(() => {
    return data.all_bets.reduce((sum, b) => sum + Number(b.bet || 0), 0);
  }, [data.all_bets]);

  const shownMultiplier =
    data.phase === "betting" ? "WAITING" : `${Number(data.multiplier || 1).toFixed(2)}x`;
  
  const[user,setUser]=useState({user_name:"DEMO123",balance:0});

  useEffect(()=>{
    fetchCurrentUser().then(setUser);
  },[]);

  return (
    <div className="mobile-aviator app">
      <header className="top">
        <div className="brand">
          <span className="home">⌂</span>
          <span>GOLD</span>
          <b>365</b>
        </div>

      <div className="profile">
        <span>🌐</span>
        <span className="balance">{Number(user.balance||0).toFixed(2)}</span>
        <UserMenuLayout/>
        <span className="user">{user.user_name||"DEMO123"}</span>
      </div>
      </header>

      <main className="layout">
        <section className="game-area">
          <div className="history-wrap">
            <div className="history">
              {[...(data.history||[])].reverse().slice(0,100).map((v,i)=>(
                <span key={i} className={historyClass(v)}>{Number(v).toFixed(2)}x</span>
              ))}
              <button className={`drop ${showHistory?"open":""}`} onClick={()=>setShowHistory(!showHistory)}>⌄</button>
            </div>
            {showHistory&&(
              <div className="history-dropdown">
                {[...(data.history||[])].reverse().map((v,i)=>(
                  <span key={i} className={historyClass(v)}>{Number(v).toFixed(2)}x</span>
                ))}
              </div>
            )}
          </div>

            <div
              className={`canvas ${
                data.phase === "betting" ? "waiting-mode" : ""
              } ${data.phase === "flying" ? "flying-mode" : ""} ${
                data.phase === "crashed" ? "crashed-mode" : ""
              } ${
                Number(data.multiplier || 1) >= 10
                  ? "hot-bg"
                  : Number(data.multiplier || 1) >= 2
                  ? "mid-bg"
                  : "low-bg"
              }`}
            >
            <div className="rays" />

            <div className="axis y">
              {[1, 2, 3, 4, 5].map((i) => (
                <span key={i}>•</span>
              ))}
            </div>

            <div className="axis x">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
                <span key={i}>•</span>
              ))}
            </div>

              {data.phase === "betting" ? (
                <div className="waiting-box">
                  <div className="loader-plane">
                    <svg viewBox="0 0 80 80">
                      <path d="M40 4 53 37 76 44 54 52 41 76 31 51 5 43 30 36z" />
                    </svg>
                    <span className="loader-ring ring-1" />
                    <span className="loader-ring ring-2" />
                    <span className="loader-ring ring-3" />
                  </div>

                  <div className="waiting-text">WAITING FOR NEXT ROUND</div>

                  <div className="timer-bar">
                    <div
                      className="timer-fill"
                      style={{
                        width: `${Math.max(
                          0,
                          Math.min(
                            100,
                            (Number(data.countdown || 0) /
                              Number(data.waiting_seconds || 30)) *
                              100
                          )
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              ): data.phase === "crashed" ? (
              <div className="crash-center">
                <div className="flew-text">FLEW AWAY!</div>
                <div className="flew-multiplier">
                  {Number(data.crashed_at || data.multiplier || 1).toFixed(2)}x
                </div>
              </div>
            ) : (
              <div className="multiplier">{shownMultiplier}</div>
            )}

            <Plane phase={data.phase} multiplier={Number(data.multiplier || 1)} />
          </div>

          <div className="round">Round Id: {data.round_id}</div>

          <div className="panels">
            <BetPanel
              seat={1}
              phase={data.phase}
              multiplier={Number(data.multiplier || 1)}
              roundId={data.round_id}
              myBets={data.my_bets || []}
              onNotice={setNotice}
            />

            <BetPanel
              seat={2}
              phase={data.phase}
              multiplier={Number(data.multiplier || 1)}
              roundId={data.round_id}
              myBets={data.my_bets || []}
              onNotice={setNotice}
            />
          </div>
        </section>
      </main>

      <div className="toast">
        {notice} <span>Total bets: {formatMoney(totalBet)}</span>
      </div>
    </div>
  );
}

export default App;
import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API = "http://localhost:8005";
const WS = "ws://localhost:8005/ws/game";

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
  const crashed = phase === "crashed";

  const left = isBetting ? 8 : Math.min(7 + multiplier * 9, 66);
  const bottom = isBetting ? 8 : Math.min(8 + multiplier * 4, 58);

  return (
    <div
      className={`plane-wrap ${isBetting ? "idle" : ""}`}
      style={{ left: `${left}%`, bottom: `${bottom}%` }}
    >
      <svg className={crashed ? "plane crash" : "plane"} viewBox="0 0 260 95">
        <path className="plane-body" d="M7 64h122l65-35c9-5 18-8 27-9l27-2 5 9-35 21-42 25H7z" />
        <path className="wing wing-top" d="M125 64 96 24h27l48 30-18 10z" />
        <path className="wing wing-left" d="M57 64 29 39h23l53 25z" />
        <path className="wing wing-bottom" d="M190 73 155 93h-38l48-28z" />
        <circle cx="216" cy="32" r="5" />
      </svg>
      <div className="trail" />
    </div>
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
      const res = await fetch(`${API}/api/bet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "demo_user", seat, amount: Number(amount) }),
      });
      const data = await res.json();
      onNotice(data.message || "Done");
    } catch {
      onNotice("Backend not connected");
    }
  }

  async function cashout() {
    try {
      const res = await fetch(`${API}/api/cashout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "demo_user", seat }),
      });
      const data = await res.json();
      onNotice(data.message || "Done");
    } catch {
      onNotice("Backend not connected");
    }
  }

  return (
    <div className="bet-panel">
      <div className="tab-switch"><button className={!auto ? "active" : ""} onClick={() => setAuto(false)}>Bet</button><button className={auto ? "active" : ""} onClick={() => setAuto(true)}>Auto</button></div>
      <div className="bet-body">
        <div className="amount-box">
          <div className="amount-input"><button onClick={() => setAmount(Math.max(10, amount - 10))}>−</button><input value={amount} onChange={(e) => setAmount(e.target.value)} /><button onClick={() => setAmount(Number(amount || 0) + 10)}>+</button></div>
          <div className="quick"><button onClick={() => setAmount(10)}>10</button><button onClick={() => setAmount(20)}>20</button><button onClick={() => setAmount(50)}>50</button><button onClick={() => setAmount(100)}>100</button></div>
        </div>
        {canCashout ? (
          <button className="bet-btn orange" onClick={cashout}>CASH OUT<br /><span>{formatMoney(Number(activeBet.amount) * multiplier)} INR</span></button>
        ) : (
          <button className="bet-btn" disabled={!canBet} onClick={placeBet}>BET<br /><span>{formatMoney(amount)} INR</span></button>
        )}
      </div>
      {activeBet && <div className={`bet-status ${activeBet.status}`}>{activeBet.status === "cashed_out" ? `Cashed out ${activeBet.cashout_multiplier}x = ${formatMoney(activeBet.cashout_amount)}` : activeBet.status === "lost" ? "Lost" : "Bet accepted"}</div>}
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
  const wsRef = useRef(null);

  useEffect(() => {
    let retry;
    function connect() {
      const ws = new WebSocket(WS);
      ws.onopen = () => setNotice("Live connected");
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.data) setData(msg.data);
      };
      ws.onclose = () => { setNotice("Reconnecting..."); retry = setTimeout(connect, 1500); };
      ws.onerror = () => setNotice("Socket error");
      wsRef.current = ws;
    }
    connect();
    return () => { clearTimeout(retry); wsRef.current?.close(); };
  }, []);

  const totalBet = useMemo(() => data.all_bets.reduce((sum, b) => sum + Number(b.bet || 0), 0), [data.all_bets]);
  const shownMultiplier = data.phase === "betting" ? "WAITING" : `${Number(data.multiplier || 1).toFixed(2)}x`;

  return (
    <div className="app">
      <header className="top"><div className="brand"><span className="home">⌂</span><span>GOLD</span><b>365</b></div><div className="profile"><span>🌐</span><span className="balance">0.00</span><span>☰</span><span className="user">DEM123</span></div></header>
      <div className="sub"><div className="aviator">AviatorX</div><button>How To Play ?</button><div className="spacer" /><span className="wifi">≋</span><span>C</span><span className="green">0.00</span><span>_</span></div>

      <main className="layout">
        <aside className="sidebar">
          <div className="tabs"><button className="active">All Bets</button><button>My Bet</button></div>
          <h3>ALL BETS</h3><div className="count">{data.all_bets.length}</div>
          <div className="table-head"><span>User</span><span>Bet(INR)</span><span>X</span><span>Cash out(INR)</span></div>
          <div className="bet-list">{data.all_bets.map((b) => <div className="row" key={b.id}><span className="u"><i>{b.avatar}</i>{b.user}</span><span>{formatMoney(b.bet)}</span><span></span><b>{formatMoney(b.cashout)}</b></div>)}</div>
          <div className="fair">This game is <u>Provably fair</u></div>
        </aside>

        <section className="game-area">
          <div className="history">{data.history.map((v, i) => <span key={i} className={historyClass(v)}>{Number(v).toFixed(2)}x</span>)}<span className="drop">⌄</span></div>
          <div className={`canvas ${data.phase === "betting" ? "waiting-mode" : ""}`}>
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
                      width: `${Math.max(0,Math.min(100, (Number(data.countdown || 0) / Number(data.waiting_seconds || 30)) * 100 ))}%`,
                    }}
                  />
                </div>

                <div className="timer-number">{data.countdown}s</div>
              </div>
            ) : (
              <div className={`multiplier ${data.phase === "crashed" ? "crashed" : ""}`}>
                {shownMultiplier}
              </div>
            )}

            {data.phase === "crashed" && (
              <div className="countdown red">
                Flew away at {Number(data.crashed_at).toFixed(2)}x
              </div>
            )}

            <Plane phase={data.phase} multiplier={Number(data.multiplier || 1)} />
          </div>
          <div className="round">Round Id: {data.round_id}</div>
          <div className="panels"><BetPanel seat={1} phase={data.phase} multiplier={Number(data.multiplier || 1)} roundId={data.round_id} myBets={data.my_bets || []} onNotice={setNotice}/><BetPanel seat={2} phase={data.phase} multiplier={Number(data.multiplier || 1)} roundId={data.round_id} myBets={data.my_bets || []} onNotice={setNotice}/></div>
        </section>
      </main>
      <div className="toast">{notice} <span>Total bets: {formatMoney(totalBet)}</span></div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);

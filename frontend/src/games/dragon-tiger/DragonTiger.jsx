import React, { useEffect, useMemo, useRef, useState } from "react";
import "./dragonTiger.css";

const API = "http://localhost:8005";
const WS = "ws://localhost:8005/ws/dragon-tiger";
const USER_ID = "demo_user";

const CHIP_VALUES = [1, 2, 5, 10, 50];

const ROAD_VALUES = [
  "D", "D", "D", "Tie", "Tie", "D", "T", "T", "D", "T", "T", "D", "D", "T", "T", "D", "Tie", "D", "T",
  "T", "D", "T", "D", "D", "T", "D", "T", "T", "Tie", "D", "D", "D", "D", "D", "D", "Tie", "D", "D",
  "T", "T", "D", "T", "T", "D", "D", "D", "D", "D", "T", "T", "D", "T", "D", "D", "D", "T", "D",
];

function formatMoney(n) {
  return Number(n || 0).toFixed(2);
}

function playWinSound() {
  const audio = new Audio("/sounds/win-roar.mp3");
  audio.volume = 0.9;
  audio.play().catch(() => {});
}

function playChipSound() {
  const audio = new Audio("/sounds/chip.mp3");
  audio.volume = 0.45;
  audio.play().catch(() => {});
}

function Card({ card, side, hidden }) {
  if (!card || hidden) {
    return (
      <div className={`dt-card ${side} back`}>
        <div className="card-corner top">✦</div>
        <span>{side === "dragon" ? "龍" : "虎"}</span>
        <div className="card-corner bottom">✦</div>
      </div>
    );
  }

  return (
    <div className={`dt-card ${side} ${card.color}`}>
      <small>{card.rank}</small>
      <b>{card.symbol}</b>
      <small>{card.rank}</small>
    </div>
  );
}

export default function DragonTiger() {
  const [data, setData] = useState({
    phase: "waiting",
    round_id: "",
    countdown: 0,
    waiting_seconds: 15,
    dragon_card: null,
    tiger_card: null,
    result: null,
    my_bets: [],
    history: [],
  });

  const [chip, setChip] = useState(1);
  const [notice, setNotice] = useState("Connecting");
  const [soundOn, setSoundOn] = useState(true);
  const lastRoundRef = useRef("");

  useEffect(() => {
    let retry;
    let ws;

    function connect() {
      ws = new WebSocket(WS);

      ws.onopen = () => setNotice("Live connected");

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (!msg.data) return;

        setData(msg.data);

        const winner = msg.data?.result?.winner;
        const round = msg.data?.round_id;

        if (msg.data.phase === "result" && winner && lastRoundRef.current !== round) {
          lastRoundRef.current = round;
          if (soundOn) playWinSound();
        }
      };

      ws.onclose = () => {
        setNotice("Reconnecting...");
        retry = setTimeout(connect, 1500);
      };

      ws.onerror = () => setNotice("Socket error");
    }

    connect();

    return () => {
      clearTimeout(retry);
      ws?.close();
    };
  }, [soundOn]);

  const betMap = useMemo(() => {
    const map = {};
    for (const bet of data.my_bets || []) {
      map[bet.bet_type] = (map[bet.bet_type] || 0) + Number(bet.amount || 0);
    }
    return map;
  }, [data.my_bets]);

  const totalBet = useMemo(
    () => (data.my_bets || []).reduce((s, b) => s + Number(b.amount || 0), 0),
    [data.my_bets]
  );

  const totalWin = useMemo(
    () => (data.my_bets || []).reduce((s, b) => s + Number(b.payout || 0), 0),
    [data.my_bets]
  );

  async function placeBet(type) {
    if (data.phase !== "betting") {
      setNotice("Betting closed");
      return;
    }

    if (soundOn) playChipSound();

    try {
      const res = await fetch(`${API}/api/games/dragon-tiger/bet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: USER_ID,
          bet_type: type,
          amount: Number(chip),
        }),
      });

      const json = await res.json();
      setNotice(json.message || "Bet placed");
    } catch {
      setNotice("Backend not connected");
    }
  }

  async function clearBets() {
    try {
      const res = await fetch(`${API}/api/games/dragon-tiger/clear`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: USER_ID }),
      });

      const json = await res.json();
      setNotice(json.message || "Cleared");
    } catch {
      setNotice("Backend not connected");
    }
  }

  const winner = data.result?.suited_tie ? "SUITED TIE" : data.result?.winner || "";
  const progress = Math.max(
    0,
    Math.min(
      100,
      (Number(data.countdown || 0) / Number(data.waiting_seconds || 15)) * 100
    )
  );

  const phaseLabel =
    data.phase === "betting"
      ? "BETS ARE CLOSING"
      : data.phase === "dealing"
      ? "DEALING"
      : data.phase === "result"
      ? "RESULT"
      : "WAITING";

  return (
    <div className="dt-page">
      <div className="dt-bg" />

      <header className="dt-topbar">
        <button className="dt-back" onClick={() => window.history.back()}>
          ‹
        </button>

        <div className="dt-logo">
          <i>♕</i>
          <span>DRAGON</span>
          <b>TIGER</b>
          <i>♕</i>
        </div>

        <div className="dt-credit">
          <small>Credits</small>
          <strong>0.00</strong>
        </div>
      </header>

      <section className="dt-info-row">
        <div>
          <span>Total Bet</span>
          <b>{formatMoney(totalBet)}</b>
        </div>
        <div>
          <span>Last Win</span>
          <b>{formatMoney(totalWin)}</b>
        </div>
        <div>
          <span>Round</span>
          <b>{data.round_id || "-"}</b>
        </div>
        <div>
          <span>Status</span>
          <b>{data.phase || "waiting"}</b>
        </div>
      </section>

      <main className="dt-layout">
        <section className="dt-table">
          <div className="dt-status">
            <b>{phaseLabel}</b>
            <span>
              <i style={{ width: `${progress}%` }} />
            </span>
          </div>

          <div className="dt-roadmap">
            {(data.history?.length ? data.history : ROAD_VALUES).slice(-57).map((item, index) => {
              const value = typeof item === "string" ? item : item?.winner || item?.result || "D";
              const label = value === "DRAGON" ? "D" : value === "TIGER" ? "T" : value;
              const cls = label === "D" ? "dragon" : label === "T" ? "tiger" : "tie";

              return (
                <span className={cls} key={index}>
                  {label}
                </span>
              );
            })}
          </div>

          <section className="dt-battle-area">
            <div className="dt-battle-overlay" />

            <h2 className="dt-side-title dragon">DRAGON</h2>
            <h2 className="dt-side-title tiger">TIGER</h2>

            <div className="dt-card-zone">
              <Card
                side="dragon"
                card={data.dragon_card}
                hidden={data.phase === "betting"}
              />

              <button className="dt-tie-orb" onClick={() => placeBet("TIE")}>
                TIE
              </button>

              <Card
                side="tiger"
                card={data.tiger_card}
                hidden={data.phase === "betting"}
              />
            </div>
          </section>

          <section className="dt-main-bets">
            <button className="dragon" onClick={() => placeBet("DRAGON")}>
              <span>DRAGON</span>
              <b>{formatMoney(betMap.DRAGON)}</b>
            </button>

            <div className="dt-tie-bets">
              <button onClick={() => placeBet("TIE")}>
                <span>TIE</span>
                <b>{formatMoney(betMap.TIE)}</b>
              </button>

              <button onClick={() => placeBet("SUITED_TIE")}>
                <span>SUITED TIE</span>
                <b>{formatMoney(betMap.SUITED_TIE)}</b>
              </button>
            </div>

            <button className="tiger" onClick={() => placeBet("TIGER")}>
              <span>TIGER</span>
              <b>{formatMoney(betMap.TIGER)}</b>
            </button>
          </section>

          <section className="dt-sub-bets">
            {["BIG", "SMALL", "ODD", "EVEN"].map((x) => (
              <button key={`D-${x}`} onClick={() => placeBet(`DRAGON_${x}`)}>
                <span>{x}</span>
                <b>{formatMoney(betMap[`DRAGON_${x}`])}</b>
              </button>
            ))}

            {["BIG", "SMALL", "ODD", "EVEN"].map((x) => (
              <button key={`T-${x}`} onClick={() => placeBet(`TIGER_${x}`)}>
                <span>{x}</span>
                <b>{formatMoney(betMap[`TIGER_${x}`])}</b>
              </button>
            ))}
          </section>

          <section className="dt-suits">
            {["♥", "♣", "♦", "♠", "♥", "♣", "♦", "♠"].map((s, i) => (
              <button
                key={i}
                onClick={() =>
                  placeBet(
                    `${i < 4 ? "DRAGON" : "TIGER"}_${
                      s === "♥"
                        ? "HEART"
                        : s === "♣"
                        ? "CLUB"
                        : s === "♦"
                        ? "DIAMOND"
                        : "SPADE"
                    }`
                  )
                }
              >
                {s}
              </button>
            ))}
          </section>
        </section>

        <aside className="dt-control-panel">
          <div className="dt-chip-row">
            {CHIP_VALUES.map((value) => (
              <button
                key={value}
                className={chip === value ? "active" : ""}
                onClick={() => setChip(value)}
              >
                {value}
              </button>
            ))}
          </div>

          <div className="dt-action-grid">
            <button>Deal</button>
            <button>Repeat</button>
            <button onClick={clearBets}>Clear</button>
            <button>Autoplay</button>
          </div>

          <div className="dt-my-title">My Bets</div>

          <div className="dt-my-bets">
            {(data.my_bets || []).length === 0 ? (
              <p>No bets yet</p>
            ) : (
              data.my_bets.map((bet, i) => (
                <div key={bet.id || i}>
                  <span>{bet.bet_type}</span>
                  <b>₹ {formatMoney(bet.amount)}</b>
                </div>
              ))
            )}
          </div>

          <button className="dt-sound" onClick={() => setSoundOn(!soundOn)}>
            {soundOn ? "🔊 Sound On" : "🔇 Sound Off"}
          </button>
        </aside>
      </main>

      {winner && (
        <div className="dt-win-effect">
          <div className="dt-fireworks" />

          <div className="dt-winner-card">
            <div className="dt-crown">♛</div>
            <h1>WINNER</h1>
            <h2>{winner}</h2>
            <p>YOU WIN</p>
            <strong>₹ {formatMoney(totalWin)}</strong>
          </div>

          {Array.from({ length: 26 }).map((_, i) => (
            <span key={i} className={`dt-coin-fall coin-${i}`}>
              ●
            </span>
          ))}
        </div>
      )}

      <div className="dt-toast">
        <span />
        {notice}
      </div>
    </div>
  );
}
import React, { useEffect, useMemo, useRef, useState } from "react";
import "./luckyRace.css";

const API = "http://localhost:8005";
const WS = "ws://localhost:8005/ws/lucky-race";

const CHIPS = [10, 50, 100, 1000, 5000, 10000];

function formatMoney(n) {
  return Number(n || 0).toFixed(2);
}

function carClass(key) {
  return String(key || "").toLowerCase().replaceAll("_", "-");
}

function PlayerCard({ player }) {
  return (
    <div className="lr-player-card">
      {player.tag && <div className={`lr-player-tag ${player.tag.toLowerCase()}`}>{player.tag}</div>}
      <div className="lr-avatar">{player.avatar}</div>
      <div className="lr-player-name">{player.name}</div>
      <div className="lr-player-balance">₹ {player.balance}</div>
    </div>
  );
}

function TrackIcon({ car, active, winner }) {
  return (
    <div className={`lr-track-icon ${carClass(car.key)} ${active ? "active" : ""} ${winner ? "winner" : ""}`}>
      <span>{car.icon}</span>
    </div>
  );
}

function ChipStack({ amount }) {
  const count = Math.min(18, Math.max(5, Math.floor(Number(amount || 0) / 500) + 5));

  return (
    <div className="lr-chip-stack">
      {Array.from({ length: count }).map((_, index) => (
        <span
          key={index}
          style={{
            left: `${8 + (index * 17) % 165}px`,
            top: `${8 + (index * 11) % 58}px`,
          }}
        >
          {index % 5 === 0 ? "100" : index % 3 === 0 ? "50" : "10"}
        </span>
      ))}
    </div>
  );
}

export default function LuckyRace() {
  const [data, setData] = useState({
    phase: "waiting",
    round_id: "",
    countdown: 0,
    waiting_seconds: 12,
    cars: [],
    winner: null,
    track_index: 0,
    history: [],
    my_bets: [],
    board_totals: {},
    players: [],
  });

  const [chip, setChip] = useState(10);
  const [notice, setNotice] = useState("");
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

  const betMap = useMemo(() => {
    const map = {};

    for (const bet of data.my_bets || []) {
      map[bet.bet_type] = (map[bet.bet_type] || 0) + Number(bet.amount || 0);
    }

    return map;
  }, [data.my_bets]);

  const totalBet = useMemo(() => {
    return (data.my_bets || []).reduce((sum, bet) => sum + Number(bet.amount || 0), 0);
  }, [data.my_bets]);

  const totalWin = useMemo(() => {
    return (data.my_bets || []).reduce((sum, bet) => sum + Number(bet.payout || 0), 0);
  }, [data.my_bets]);

  async function placeBet(carKey) {
    if (data.phase !== "betting") {
      setNotice("Betting closed");
      return;
    }

    try {
      const res = await fetch(`${API}/api/games/lucky-race/bet`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: "demo_user",
          bet_type: carKey,
          amount: Number(chip),
        }),
      });

      const json = await res.json();
      setNotice(json.message || "Done");
    } catch {
      setNotice("Backend not connected");
    }
  }

  async function clearBets() {
    try {
      const res = await fetch(`${API}/api/games/lucky-race/clear`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: "demo_user",
        }),
      });

      const json = await res.json();
      setNotice(json.message || "Done");
    } catch {
      setNotice("Backend not connected");
    }
  }

  const progress = Math.max(
    0,
    Math.min(100, (Number(data.countdown || 0) / Number(data.waiting_seconds || 12)) * 100)
  );

  const players = data.players || [];
  const leftPlayers = players.slice(0, 3);
  const rightPlayers = players.slice(3, 6);

  const trackCars = [...(data.cars || []), ...(data.cars || []), ...(data.cars || [])];

  return (
    <div className="lr-app">
      <header className="lr-top">
        <a href="/" className="lr-icon-button">‹</a>
        <button className="lr-icon-button">i</button>

        <div className="lr-title">
          <span>Lucky</span>
          <b>Car Roulette</b>
        </div>

        <button className="lr-add">
          ADD <span>₹</span>
        </button>
      </header>

      <main className="lr-main">
        <aside className="lr-side lr-left">
          {leftPlayers.map((player, index) => (
            <PlayerCard key={index} player={player} />
          ))}
        </aside>

        <section className="lr-game">
          <div className="lr-track-wrap">
            <div className="lr-track">
              {trackCars.map((car, index) => {
                const active = data.phase === "spinning" && index % (data.cars.length || 1) === data.track_index;
                const winner = data.phase === "result" && data.winner?.key === car.key;

                return (
                  <TrackIcon
                    key={`${car.key}-${index}`}
                    car={car}
                    active={active}
                    winner={winner}
                  />
                );
              })}
            </div>

            <div className="lr-center-machine">
              <div className="lr-lucky">Lucky</div>
              <div className="lr-count">
                {data.phase === "betting"
                  ? data.countdown
                  : data.phase === "spinning"
                  ? "GO"
                  : data.winner?.icon || "★"}
              </div>
            </div>

            {data.phase === "betting" && (
              <div className="lr-progress">
                <div style={{ width: `${progress}%` }} />
              </div>
            )}
          </div>

          <div className="lr-status">
            {data.phase === "betting" && "PLACE YOUR BETS"}
            {data.phase === "spinning" && "SPINNING..."}
            {data.phase === "result" && `WINNER: ${data.winner?.label}`}
          </div>

          <div className="lr-board">
            {(data.cars || []).map((car) => {
              const totals = data.board_totals?.[car.key] || { my: 0, total: 0 };
              const isWinner = data.phase === "result" && data.winner?.key === car.key;
              const myAmount = betMap[car.key] || 0;

              return (
                <button
                  key={car.key}
                  className={`lr-bet-box ${carClass(car.key)} ${isWinner ? "winner" : ""}`}
                  onClick={() => placeBet(car.key)}
                >
                  <div className="lr-bet-head">
                    <span>{car.icon}</span>
                    <b>{car.label}</b>
                    <em>{car.payout}x</em>
                  </div>

                  <div className="lr-bet-total">
                    {formatMoney(myAmount)} / {formatMoney(totals.total)}
                  </div>

                  <ChipStack amount={totals.total} />

                  {isWinner && <div className="lr-winner-star">★</div>}
                </button>
              );
            })}
          </div>
        </section>

        <aside className="lr-side lr-right">
          {rightPlayers.map((player, index) => (
            <PlayerCard key={index} player={player} />
          ))}
        </aside>
      </main>

      <footer className="lr-bottom">
        <div className="lr-chat">💬</div>

        <div className="lr-online">👥 1160</div>

        <div className="lr-user">
          <div className="lr-user-avatar">👨</div>
          <div>
            <span>player_...</span>
            <b>₹ 17.35</b>
          </div>
        </div>

        <div className="lr-chips">
          {CHIPS.map((value) => (
            <button
              key={value}
              className={chip === value ? "active" : ""}
              onClick={() => setChip(value)}
            >
              {value}
            </button>
          ))}
        </div>

        <button className="lr-clear" onClick={clearBets}>
          CLEAR
        </button>

        <div className="lr-trend">↗</div>
      </footer>

      <div className="lr-toast">
        {notice}
        <span> Bet: ₹{formatMoney(totalBet)}</span>
        <span> Win: ₹{formatMoney(totalWin)}</span>
      </div>
    </div>
  );
}
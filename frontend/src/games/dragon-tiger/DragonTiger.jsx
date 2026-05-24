import React, { useEffect, useMemo, useRef, useState } from "react";
import "./dragonTiger.css";

const API = "http://localhost:8005";
const WS = "ws://localhost:8005/ws/dragon-tiger";

const CHIP_VALUES = [1, 2, 5, 10, 50];

const BETS = [
  { key: "DRAGON", label: "DRAGON", group: "main" },
  { key: "TIE", label: "TIE", group: "tie" },
  { key: "SUITED_TIE", label: "SUITED TIE", group: "tie" },
  { key: "TIGER", label: "TIGER", group: "main" },

  { key: "DRAGON_BIG", label: "Big", group: "dragon-extra" },
  { key: "DRAGON_SMALL", label: "Small", group: "dragon-extra" },
  { key: "DRAGON_ODD", label: "Odd", group: "dragon-extra" },
  { key: "DRAGON_EVEN", label: "Even", group: "dragon-extra" },

  { key: "TIGER_BIG", label: "Big", group: "tiger-extra" },
  { key: "TIGER_SMALL", label: "Small", group: "tiger-extra" },
  { key: "TIGER_ODD", label: "Odd", group: "tiger-extra" },
  { key: "TIGER_EVEN", label: "Even", group: "tiger-extra" },

  { key: "DRAGON_HEART", label: "♥", group: "dragon-suit" },
  { key: "DRAGON_CLUB", label: "♣", group: "dragon-suit" },
  { key: "DRAGON_DIAMOND", label: "♦", group: "dragon-suit" },
  { key: "DRAGON_SPADE", label: "♠", group: "dragon-suit" },

  { key: "TIGER_HEART", label: "♥", group: "tiger-suit" },
  { key: "TIGER_CLUB", label: "♣", group: "tiger-suit" },
  { key: "TIGER_DIAMOND", label: "♦", group: "tiger-suit" },
  { key: "TIGER_SPADE", label: "♠", group: "tiger-suit" },
];

function formatMoney(n) {
  return Number(n || 0).toFixed(2);
}

function Card({ card, side, hidden }) {
  if (!card || hidden) {
    return (
      <div className={`dt-card ${side}`}>
        <div className="card-back">★</div>
      </div>
    );
  }

  return (
    <div className={`dt-card ${side} ${card.color}`}>
      <div className="card-rank">{card.rank}</div>
      <div className="card-suit">{card.symbol}</div>
      <div className="card-rank bottom">{card.rank}</div>
    </div>
  );
}

function RoadMap({ history }) {
  const cells = Array.from({ length: 66 }, (_, i) => history[i] || null);

  return (
    <div className="dt-roadmap">
      {cells.map((item, index) => {
        if (!item) return <span key={index} />;

        const cls =
          item.winner === "DRAGON"
            ? "dragon"
            : item.winner === "TIGER"
            ? "tiger"
            : "tie";

        return (
          <span key={index} className={cls}>
            {item.winner === "DRAGON" ? "D" : item.winner === "TIGER" ? "T" : "Tie"}
          </span>
        );
      })}
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
    history: [],
    my_bets: [],
    total_bet: 0,
  });

  const [chip, setChip] = useState(1);
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

  const totalUserBet = useMemo(() => {
    return (data.my_bets || []).reduce((sum, b) => sum + Number(b.amount || 0), 0);
  }, [data.my_bets]);

  const totalWin = useMemo(() => {
    return (data.my_bets || []).reduce((sum, b) => sum + Number(b.payout || 0), 0);
  }, [data.my_bets]);

  async function placeBet(betType) {
    if (data.phase !== "betting") {
      setNotice("Betting closed");
      return;
    }

    try {
      const res = await fetch(`${API}/api/games/dragon-tiger/bet`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: "demo_user",
          bet_type: betType,
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
      const res = await fetch(`${API}/api/games/dragon-tiger/clear`, {
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
    Math.min(100, (Number(data.countdown || 0) / Number(data.waiting_seconds || 15)) * 100)
  );

  const resultText = data.result
    ? data.result.suited_tie
      ? "SUITED TIE"
      : data.result.winner
    : "";

  return (
    <div className="dt-app">
      <header className="dt-top">
        <a href="/aviator" className="dt-back">
          ‹
        </a>

        <div className="dt-title">
          <span>DRAGON</span>
          <b>TIGER</b>
        </div>

        <div className="dt-wallet">
          <span>Credits</span>
          <b>0.00</b>
        </div>
      </header>

      <section className="dt-stats">
        <div>
          <span>Total Bet</span>
          <b>{formatMoney(totalUserBet)}</b>
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
          <b>{data.phase}</b>
        </div>
      </section>

      <main className="dt-layout">
        <section className="dt-board">
          <div className="dt-timer">
            <div className="dt-timer-label">
              {data.phase === "betting"
                ? "BETS ARE CLOSING"
                : data.phase === "dealing"
                ? "DEALING CARDS"
                : data.phase === "result"
                ? "RESULT"
                : "WAITING"}
            </div>

            {data.phase === "betting" && (
              <div className="dt-progress">
                <div style={{ width: `${progress}%` }} />
              </div>
            )}
          </div>

          <RoadMap history={[...(data.history || [])].reverse()} />

          <div className="dt-card-stage">
            <div className="dt-side-title dragon">DRAGON</div>

            <Card
              side="dragon"
              card={data.dragon_card}
              hidden={data.phase === "betting"}
            />

            <div className="dt-result-circle">
              {data.phase === "result" ? resultText : "TIE"}
            </div>

            <Card
              side="tiger"
              card={data.tiger_card}
              hidden={data.phase === "betting" || !data.tiger_card}
            />

            <div className="dt-side-title tiger">TIGER</div>
          </div>

          <div className="dt-betting-grid">
            <button className="dt-bet-main dragon" onClick={() => placeBet("DRAGON")}>
              <span>DRAGON</span>
              <b>{formatMoney(betMap.DRAGON)}</b>
            </button>

            <div className="dt-tie-stack">
              <button onClick={() => placeBet("TIE")}>
                TIE <b>{formatMoney(betMap.TIE)}</b>
              </button>
              <button onClick={() => placeBet("SUITED_TIE")}>
                SUITED TIE <b>{formatMoney(betMap.SUITED_TIE)}</b>
              </button>
            </div>

            <button className="dt-bet-main tiger" onClick={() => placeBet("TIGER")}>
              <span>TIGER</span>
              <b>{formatMoney(betMap.TIGER)}</b>
            </button>
          </div>

          <div className="dt-side-bets">
            <div>
              {BETS.filter((b) => b.group === "dragon-extra").map((b) => (
                <button key={b.key} onClick={() => placeBet(b.key)}>
                  {b.label}
                  <span>{formatMoney(betMap[b.key])}</span>
                </button>
              ))}
            </div>

            <div>
              {BETS.filter((b) => b.group === "tiger-extra").map((b) => (
                <button key={b.key} onClick={() => placeBet(b.key)}>
                  {b.label}
                  <span>{formatMoney(betMap[b.key])}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="dt-suits">
            <div>
              {BETS.filter((b) => b.group === "dragon-suit").map((b) => (
                <button
                  key={b.key}
                  className={b.label === "♥" || b.label === "♦" ? "red" : ""}
                  onClick={() => placeBet(b.key)}
                >
                  {b.label}
                </button>
              ))}
            </div>

            <div>
              {BETS.filter((b) => b.group === "tiger-suit").map((b) => (
                <button
                  key={b.key}
                  className={b.label === "♥" || b.label === "♦" ? "red" : ""}
                  onClick={() => placeBet(b.key)}
                >
                  {b.label}
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="dt-controls">
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

          <div className="dt-action-row">
            <button>Deal</button>
            <button>Repeat</button>
            <button onClick={clearBets}>Clear</button>
            <button>Autoplay</button>
          </div>

          <div className="dt-my-bets">
            <h3>My Bets</h3>

            {(data.my_bets || []).length === 0 && <p>No bets yet</p>}

            {(data.my_bets || []).map((bet) => (
              <div key={bet.id} className={`dt-my-bet ${bet.status}`}>
                <span>{bet.bet_type}</span>
                <b>{formatMoney(bet.amount)}</b>
                <em>{bet.status}</em>
                <strong>{formatMoney(bet.payout)}</strong>
              </div>
            ))}
          </div>
        </section>
      </main>

      <div className="dt-toast">{notice}</div>
    </div>
  );
}
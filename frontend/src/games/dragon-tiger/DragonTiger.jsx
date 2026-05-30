import React, { useEffect, useMemo, useRef, useState } from "react";
import "./dragonTiger.css";

const API = "http://localhost:8005";
const WS = "ws://localhost:8005/ws/dragon-tiger";
const USER_ID = "demo_user";
const CHIP_VALUES = [1, 5, 10, 50, 100];

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

function TopBar({ soundOn, setSoundOn }) {
  return (
    <header className="dt-topbar">
      <a href="/aviator" className="dt-back">‹</a>
      <div className="dt-logo">
        <span>DRAGON</span>
        <em>VS</em>
        <b>TIGER</b>
      </div>
      <button className="dt-sound" onClick={() => setSoundOn(!soundOn)}>
        {soundOn ? "🔊" : "🔇"}
      </button>
    </header>
  );
}

function StatusPill({ phaseText, countdown, progress, roundId }) {
  return (
    <div className="dt-status-card">
      <span>{phaseText}</span>
      <strong>{String(countdown || 0).padStart(2, "0")}</strong>
      <small>ROUND: {roundId || "-"}</small>
      <div className="dt-progress"><i style={{ width: `${progress}%` }} /></div>
    </div>
  );
}

function PlayingCard({ card, side, hidden }) {
  if (!card || hidden) {
    return (
      <div className={`dt-playing-card ${side} back`}>
        <i>{side === "dragon" ? "龍" : "虎"}</i>
      </div>
    );
  }

  return (
    <div className={`dt-playing-card ${side} ${card.color}`}>
      <span>{card.rank}</span>
      <b>{card.symbol}</b>
      <span>{card.rank}</span>
    </div>
  );
}


function ResultHistory({ history }) {
  const fallback = ["D", "D", "T", "Tie", "T", "D", "T", "T", "D", "Tie", "D", "T", "D", "T", "D", "D", "T", "Tie", "D", "T", "T", "D", "D", "T", "Tie", "D", "T", "D", "T", "D", "Tie", "T", "D", "D", "T", "D", "Tie", "D", "T", "D", "T", "T", "D", "D", "T", "D", "D", "T", "Tie", "D", "T", "D", "T", "D", "D", "T", "D", "T", "D", "Tie"];
  const list = (history && history.length ? history : fallback).slice(-60);

  return (
    <section className="dt-history-panel">
      <div className="dt-history-title">BETS ARE CLOSING</div>
      <div className="dt-history-loader"><i /></div>
      <div className="dt-history-grid">
        {list.map((item, index) => {
          const value = item === "SUITED TIE" ? "Tie" : item;
          const cls = value === "D" || value === "DRAGON" ? "dragon" : value === "T" || value === "TIGER" ? "tiger" : "tie";
          const label = value === "DRAGON" ? "D" : value === "TIGER" ? "T" : value;
          return <span key={`${label}-${index}`} className={cls}>{label}</span>;
        })}
      </div>
    </section>
  );
}

function RoundInfoBar({ data, totalBet, totalWin, phaseText }) {
  return (
    <section className="dt-info-row">
      <div><span>Total Bet</span><b>{formatMoney(totalBet)}</b></div>
      <div><span>Last Win</span><b>{formatMoney(totalWin)}</b></div>
      <div><span>Round</span><b>{data.round_id || "-"}</b></div>
      <div><span>Status</span><b>{phaseText}</b></div>
    </section>
  );
}

function HeroPanel({ data, winner, totalWin, progress, phaseText }) {
  return (
    <section className="dt-hero-panel">
      <div className="dt-creature dt-dragon-img" />
      <div className="dt-creature dt-tiger-img" />
      <div className="dt-hero-vignette" />

      <h1 className="dt-dragon-title">DRAGON</h1>
      <h1 className="dt-tiger-title">TIGER</h1>

      <div className="dt-card-stage">
        <PlayingCard side="dragon" card={data.dragon_card} hidden={data.phase === "betting"} />
        <div className="dt-vs-orb">VS</div>
        <PlayingCard side="tiger" card={data.tiger_card} hidden={data.phase === "betting"} />
      </div>

      <StatusPill
        phaseText={phaseText}
        countdown={data.countdown}
        progress={progress}
        roundId={data.round_id}
      />

      {winner && (
        <div className="dt-mini-winner">
          <span>WINNER</span>
          <b>{winner}</b>
          <em>YOU WON ₹ {formatMoney(totalWin)}</em>
        </div>
      )}
    </section>
  );
}

function BetBox({ type, title, amount, rate, onClick, small = false, badge }) {
  return (
    <button className={`dt-bet-box ${type} ${small ? "small" : ""}`} onClick={onClick}>
      <div className="dt-bet-shine" />
      {badge && <em className="dt-bet-badge">{badge}</em>}
      <div className="dt-bet-corner lt" />
      <div className="dt-bet-corner rt" />
      <div className="dt-bet-corner lb" />
      <div className="dt-bet-corner rb" />
      <span>{title}</span>
      {rate && <small>{rate}</small>}
      <b>₹ {formatMoney(amount)}</b>
    </button>
  );
}

function MainBets({ betMap, placeBet }) {
  return (
    <section className="dt-main-bets-new">
      <BetBox type="dragon" title="DRAGON" badge="DRAGON" amount={betMap.DRAGON} onClick={() => placeBet("DRAGON")} />

      <div className="dt-tie-stack">
        <BetBox type="tie" title="TIE" rate="8 : 1" amount={betMap.TIE} small onClick={() => placeBet("TIE")} />
        <BetBox type="tie" title="SUITED TIE" rate="50 : 1" amount={betMap.SUITED_TIE} small onClick={() => placeBet("SUITED_TIE")} />
      </div>

      <BetBox type="tiger" title="TIGER" badge="TIGER" amount={betMap.TIGER} onClick={() => placeBet("TIGER")} />
    </section>
  );
}

function SideBets({ betMap, placeBet }) {
  const opts = ["BIG", "SMALL", "ODD", "EVEN"];

  return (
    <section className="dt-side-bets-new">
      {opts.map((x) => (
        <BetBox
          key={`D-${x}`}
          type="sub-dragon"
          title={x}
          rate="1 : 1"
          amount={betMap[`DRAGON_${x}`]}
          small
          onClick={() => placeBet(`DRAGON_${x}`)}
        />
      ))}

      {opts.map((x) => (
        <BetBox
          key={`T-${x}`}
          type="sub-tiger"
          title={x}
          rate="1 : 1"
          amount={betMap[`TIGER_${x}`]}
          small
          onClick={() => placeBet(`TIGER_${x}`)}
        />
      ))}
    </section>
  );
}

function SuitBets({ placeBet }) {
  const suits = ["♥", "♣", "♦", "♠", "♥", "♣", "♦", "♠"];

  return (
    <section className="dt-suit-bets-new">
      {suits.map((s, i) => (
        <button
          key={i}
          onClick={() =>
            placeBet(
              `${i < 4 ? "DRAGON" : "TIGER"}_${
                s === "♥" ? "HEART" : s === "♣" ? "CLUB" : s === "♦" ? "DIAMOND" : "SPADE"
              }`
            )
          }
        >
          {s}
        </button>
      ))}
    </section>
  );
}

function ChipPanel({ chip, setChip, clearBets }) {
  return (
    <footer className="dt-chip-panel-new">
      <button className="dt-action-btn" onClick={clearBets}>CLEAR</button>
      <div className="dt-chip-list">
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
      <button className="dt-action-btn confirm">BET</button>
    </footer>
  );
}

function WinEffect({ winner, totalWin }) {
  if (!winner) return null;

  return (
    <div className="dt-win-effect-new">
      <div className="dt-win-burst" />
      <div className="dt-win-card-new">
        <div className="dt-crown">♛</div>
        <h1>WINNER</h1>
        <h2>{winner}</h2>
        <p>YOU WON ₹ {formatMoney(totalWin)}</p>
      </div>
      {Array.from({ length: 28 }).map((_, i) => (
        <span key={i} className={`dt-coin-fall coin-${i}`}>●</span>
      ))}
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
  });

  const [chip, setChip] = useState(1);
  const [notice, setNotice] = useState("");
  const [soundOn, setSoundOn] = useState(true);
  const [resultHistory, setResultHistory] = useState([]);
  const lastRoundRef = useRef("");

  useEffect(() => {
    let retry;
    let ws;

    function connect() {
      ws = new WebSocket(WS);

      ws.onopen = () => setNotice("Live Connected");

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (!msg.data) return;

        setData(msg.data);

        const winner = msg.data?.result?.winner;
        const round = msg.data?.round_id;

        if (msg.data.phase === "result" && winner && lastRoundRef.current !== round) {
          lastRoundRef.current = round;
          const resultText = msg.data?.result?.suited_tie ? "SUITED TIE" : winner;
          setResultHistory((old) => [...old, resultText].slice(-60));
          if (soundOn) playWinSound();
        }
      };

      ws.onclose = () => {
        setNotice("Reconnecting...");
        retry = setTimeout(connect, 1500);
      };

      ws.onerror = () => setNotice("Socket Error");
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

  const totalWin = useMemo(
    () => (data.my_bets || []).reduce((s, b) => s + Number(b.payout || 0), 0),
    [data.my_bets]
  );

  const totalBet = useMemo(
    () => (data.my_bets || []).reduce((s, b) => s + Number(b.amount || 0), 0),
    [data.my_bets]
  );

  async function placeBet(type) {
    if (data.phase !== "betting") {
      setNotice("Betting Closed");
      return;
    }

    if (soundOn) playChipSound();

    try {
      const res = await fetch(`${API}/api/games/dragon-tiger/bet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: USER_ID, bet_type: type, amount: Number(chip) }),
      });

      const json = await res.json();
      setNotice(json.message || "Bet Placed");
    } catch {
      setNotice("Backend Not Connected");
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
      setNotice("Backend Not Connected");
    }
  }

  const winner = data.result?.suited_tie ? "SUITED TIE" : data.result?.winner || "";
  const progress = Math.max(
    0,
    Math.min(100, (Number(data.countdown || 0) / Number(data.waiting_seconds || 15)) * 100)
  );

  const phaseText =
    data.phase === "betting"
      ? "BETTING"
      : data.phase === "dealing"
      ? "DEALING"
      : data.phase === "result"
      ? "RESULT"
      : "WAITING";

  return (
    <div className={`dt-page-new ${winner ? "result-on" : ""}`}>
      <div className="dt-bg-new" />

      <TopBar soundOn={soundOn} setSoundOn={setSoundOn} />

      <main className="dt-shell-new">
        <section className="dt-board-new">
          <RoundInfoBar data={data} totalBet={totalBet} totalWin={totalWin} phaseText={phaseText} />
          <ResultHistory history={resultHistory} />
          <HeroPanel
            data={data}
            winner={winner}
            totalWin={totalWin}
            progress={progress}
            phaseText={phaseText}
          />

          <MainBets betMap={betMap} placeBet={placeBet} />
          <SideBets betMap={betMap} placeBet={placeBet} />
          <SuitBets placeBet={placeBet} />
        </section>
      </main>

      <ChipPanel chip={chip} setChip={setChip} clearBets={clearBets} />
      <WinEffect winner={winner} totalWin={totalWin} />

      <div className="dt-toast-new">{notice}</div>
    </div>
  );
}
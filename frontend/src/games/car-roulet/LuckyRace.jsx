import React, { useEffect, useMemo, useRef, useState } from "react";
import "./luckyRace.css";

const API = "http://localhost:8005";
const WS = "ws://localhost:8005/ws/lucky-race";
const CHIPS = [10, 50, 100, 1000, 5000, 10000];

const FALLBACK_CARS = [
  { key: "BMW", label: "BMW", icon: "B", payout: 6 },
  { key: "AUDI", label: "AUDI", icon: "A", payout: 6 },
  { key: "TATA", label: "TATA", icon: "T", payout: 6 },
  { key: "MERCEDES", label: "MERCEDES", icon: "M", payout: 6 },
  { key: "FERRARI", label: "FERRARI", icon: "F", payout: 6 },
  { key: "PORSCHE", label: "PORSCHE", icon: "P", payout: 6 },
  { key: "MAHINDRA", label: "MAHINDRA", icon: "M", payout: 6 },
  { key: "LUCKY", label: "LUCKY", icon: "★", payout: 12 },
];

const FALLBACK_TRACK = [
  "PORSCHE", "BMW", "MAHINDRA", "AUDI", "TATA", "LUCKY",
  "BMW", "MAHINDRA", "AUDI", "TATA", "MERCEDES", "FERRARI",
  "PORSCHE", "MERCEDES", "BMW", "MAHINDRA", "AUDI", "TATA",
  "MERCEDES", "FERRARI", "PORSCHE", "LUCKY", "FERRARI", "MERCEDES",
].map((key) => FALLBACK_CARS.find((car) => car.key === key));

function formatMoney(value) {
  return Number(value || 0).toFixed(2);
}

function carClass(key) {
  return String(key || "").toLowerCase().replaceAll("_", "-");
}

function PlayerCard({ player }) {
  return (
    <div className="lr-player-card">
      {player?.tag && (
        <div className={`lr-player-tag ${String(player.tag).toLowerCase()}`}>
          {player.tag}
        </div>
      )}
      <div className="lr-avatar">{player?.avatar || "👤"}</div>
      <div className="lr-player-name">{player?.name || "player"}</div>
      <div className="lr-player-balance">₹ {player?.balance || "0.00"}</div>
    </div>
  );
}

function BoardLogo({ car }) {
  const logoSrc = `/car-logos/${String(car.key).toLowerCase()}.png`;

  return (
    <span className="lr-board-logo">
      <img
        src={logoSrc}
        alt={car.label}
        onError={(e) => {
          e.currentTarget.style.display = "none";
          const fallback = e.currentTarget.nextSibling;
          if (fallback) fallback.style.display = "grid";
        }}
      />
      <em>{car.icon}</em>
    </span>
  );
}

function ChipStack({ amount }) {
  const count = Math.min(22, Math.max(8, Math.floor(Number(amount || 0) / 500) + 8));

  return (
    <div className="lr-chip-stack">
      {Array.from({ length: count }).map((_, index) => (
        <span
          key={index}
          style={{
            left: `${8 + (index * 19) % 185}px`,
            top: `${8 + (index * 13) % 58}px`,
          }}
        >
          {index % 5 === 0 ? "100" : index % 3 === 0 ? "50" : "10"}
        </span>
      ))}
    </div>
  );
}

function LuckyTrackCanvas({ data, progress }) {
  const canvasRef = useRef(null);
  const logosRef = useRef({});

  useEffect(() => {
    const keys = ["bmw", "audi", "tata", "mercedes", "ferrari", "porsche", "mahindra", "lucky"];

    keys.forEach((key) => {
      const img = new Image();
      img.src = `/car-logos/${key}.png`;
      logosRef.current[key.toUpperCase()] = img;
    });
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const parent = canvas.parentElement;
    const ctx = canvas.getContext("2d");
    let raf = 0;

    const positions = [
      [0.08, 0.23], [0.16, 0.15], [0.25, 0.14], [0.34, 0.15],
      [0.44, 0.15], [0.53, 0.15], [0.63, 0.15], [0.72, 0.15],
      [0.81, 0.15], [0.90, 0.23], [0.96, 0.44], [0.92, 0.68],
      [0.82, 0.78], [0.72, 0.78], [0.63, 0.78], [0.53, 0.78],
      [0.44, 0.78], [0.34, 0.78], [0.25, 0.78], [0.16, 0.78],
      [0.08, 0.68], [0.04, 0.44], [0.04, 0.32], [0.08, 0.23],
    ];

    function roundRect(x, y, w, h, r) {
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.lineTo(x + w - r, y);
      ctx.quadraticCurveTo(x + w, y, x + w, y + r);
      ctx.lineTo(x + w, y + h - r);
      ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
      ctx.lineTo(x + r, y + h);
      ctx.quadraticCurveTo(x, y + h, x, y + h - r);
      ctx.lineTo(x, y + r);
      ctx.quadraticCurveTo(x, y, x + r, y);
      ctx.closePath();
    }

    function drawLogoSlot(x, y, car, isActive, isWinner, t) {
      const key = String(car.key || "").toUpperCase();
      const logo = logosRef.current[key];

      ctx.save();

      if (isActive || isWinner) {
        const pulse = 1 + Math.sin(t / 120) * 0.08;
        ctx.translate(x, y);
        ctx.scale(pulse, pulse);
        ctx.translate(-x, -y);

        const glow = ctx.createRadialGradient(x, y, 8, x, y, 50);
        glow.addColorStop(0, "rgba(255, 245, 60, 0.95)");
        glow.addColorStop(0.45, "rgba(255, 216, 0, 0.45)");
        glow.addColorStop(1, "rgba(255, 216, 0, 0)");

        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(x, y, 54, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = "#fff157";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(x, y, 40, 0, Math.PI * 2);
        ctx.stroke();

        ctx.fillStyle = "#fff157";
        ctx.font = "900 28px Arial";
        ctx.shadowColor = "#fff157";
        ctx.shadowBlur = 14;
        ctx.fillText("★", x + 28, y - 24);
        ctx.shadowBlur = 0;
      }

      const outer = ctx.createLinearGradient(x - 35, y - 35, x + 35, y + 35);
      outer.addColorStop(0, "#74778f");
      outer.addColorStop(1, "#151621");

      ctx.fillStyle = outer;
      ctx.beginPath();
      ctx.arc(x, y, 35, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = isWinner ? "#ffffff" : isActive ? "#fff157" : "#8b8fa4";
      ctx.lineWidth = 4;
      ctx.stroke();

      ctx.fillStyle = "#10111b";
      ctx.beginPath();
      ctx.arc(x, y, 28, 0, Math.PI * 2);
      ctx.fill();

      if (logo && logo.complete && logo.naturalWidth > 0) {
        ctx.drawImage(logo, x - 24, y - 24, 48, 48);
      } else {
        ctx.fillStyle = "#ffffff";
        ctx.font = "900 20px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(car.icon || key[0] || "?", x, y);
      }

      ctx.restore();
    }

    function draw(t = 0) {
      const rect = parent.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const w = Math.max(1, rect.width);
      const h = Math.max(1, rect.height);

      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      const bg = ctx.createLinearGradient(0, 0, 0, h);
      bg.addColorStop(0, "#1b0d4a");
      bg.addColorStop(0.48, "#13072e");
      bg.addColorStop(1, "#070712");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, w, h);

      const centerGlow = ctx.createRadialGradient(w / 2, h * 0.54, 20, w / 2, h * 0.54, w * 0.44);
      centerGlow.addColorStop(0, "rgba(112, 67, 255, 0.95)");
      centerGlow.addColorStop(0.45, "rgba(80, 50, 230, 0.38)");
      centerGlow.addColorStop(1, "rgba(80, 50, 230, 0)");
      ctx.fillStyle = centerGlow;
      ctx.fillRect(0, 0, w, h);

      ctx.fillStyle = "rgba(100, 100, 255, 0.18)";
      ctx.beginPath();
      ctx.moveTo(w * 0.48, h * 0.38);
      ctx.lineTo(w * 0.04, h * 0.18);
      ctx.lineTo(w * 0.04, h * 0.80);
      ctx.lineTo(w * 0.48, h * 0.62);
      ctx.closePath();
      ctx.fill();

      ctx.beginPath();
      ctx.moveTo(w * 0.52, h * 0.38);
      ctx.lineTo(w * 0.96, h * 0.18);
      ctx.lineTo(w * 0.96, h * 0.80);
      ctx.lineTo(w * 0.52, h * 0.62);
      ctx.closePath();
      ctx.fill();

      ctx.strokeStyle = "rgba(210, 220, 255, 0.34)";
      ctx.lineWidth = 3;
      roundRect(w * 0.03, h * 0.08, w * 0.94, h * 0.84, 92);
      ctx.stroke();

      ctx.strokeStyle = "rgba(140, 155, 210, 0.26)";
      ctx.lineWidth = 2;
      roundRect(w * 0.065, h * 0.23, w * 0.87, h * 0.58, 70);
      ctx.stroke();

      const mx = w / 2 - 170;
      const my = h * 0.29;
      const mw = 340;
      const mh = 116;

      ctx.fillStyle = "rgba(5, 7, 18, 0.95)";
      ctx.strokeStyle = "rgba(100, 105, 145, 0.75)";
      ctx.lineWidth = 4;
      roundRect(mx, my, mw, mh, 48);
      ctx.fill();
      ctx.stroke();

      [mx + 94, mx + mw - 94].forEach((sx) => {
        ctx.fillStyle = "#101a4a";
        ctx.beginPath();
        ctx.arc(sx, my + 62, 42, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "rgba(85, 95, 155, 0.85)";
        ctx.lineWidth = 4;
        ctx.stroke();
        ctx.fillStyle = "#2b42b5";
        ctx.beginPath();
        ctx.arc(sx, my + 62, 12, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.fillStyle = "#d5a400";
      roundRect(w / 2 - 72, my - 31, 144, 52, 10);
      ctx.fill();
      ctx.strokeStyle = "#fff157";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = "#ffffff";
      ctx.font = "900 26px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.shadowColor = "rgba(0,0,0,0.8)";
      ctx.shadowBlur = 4;
      ctx.fillText("Lucky", w / 2, my - 5);
      ctx.shadowBlur = 0;

      if (data.phase === "betting") {
        ctx.fillStyle = "#b28cff";
        ctx.font = "900 76px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.shadowColor = "#b28cff";
        ctx.shadowBlur = 22;
        ctx.fillText(String(data.countdown || 0), w / 2, my + 68);
        ctx.shadowBlur = 0;

        const px = w * 0.38;
        const py = h - 28;
        const pw = w * 0.24;
        const ph = 7;
        ctx.fillStyle = "rgba(0,0,0,0.55)";
        roundRect(px, py, pw, ph, 8);
        ctx.fill();

        const grad = ctx.createLinearGradient(px, py, px + pw, py);
        grad.addColorStop(0, "#ffe600");
        grad.addColorStop(1, "#17ff75");
        ctx.fillStyle = grad;
        roundRect(px, py, (pw * progress) / 100, ph, 8);
        ctx.fill();
      }

      const track = data.track?.length ? data.track : FALLBACK_TRACK;

      track.forEach((car, index) => {
        const p = positions[index % positions.length];
        const x = p[0] * w;
        const y = p[1] * h;
        const active = data.phase === "spinning" && index === data.track_index;
        const winner =
          data.phase === "result" &&
          index === data.track_index &&
          data.winner?.key === car.key;

        drawLogoSlot(x, y, car, active, winner, t);
      });

      if (data.phase === "result" && data.winner) {
        ctx.fillStyle = "rgba(7, 8, 18, 0.76)";
        roundRect(w / 2 - 110, h / 2 - 38, 220, 76, 18);
        ctx.fill();
        ctx.strokeStyle = "rgba(255, 240, 87, 0.85)";
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = "#ff3b58";
        ctx.font = "900 13px Arial";
        ctx.textAlign = "center";
        ctx.fillText("WINNER", w / 2, h / 2 - 10);
        ctx.fillStyle = "#fff157";
        ctx.font = "900 26px Arial";
        ctx.fillText(data.winner.label, w / 2, h / 2 + 20);
      }

      raf = requestAnimationFrame(draw);
    }

    draw();
    return () => cancelAnimationFrame(raf);
  }, [data, progress]);

  return <canvas ref={canvasRef} className="lr-canvas-track" />;
}

export default function LuckyRace() {
  const [data, setData] = useState({
    phase: "betting",
    round_id: "",
    countdown: 12,
    waiting_seconds: 12,
    cars: FALLBACK_CARS,
    track: FALLBACK_TRACK,
    winner: null,
    track_index: 0,
    history: [],
    my_bets: [],
    board_totals: {},
    players: [],
  });

  const [chip, setChip] = useState(10);
  const [notice, setNotice] = useState("Connecting...");
  const wsRef = useRef(null);

  useEffect(() => {
    let retry = null;

    function connect() {
      const ws = new WebSocket(WS);

      ws.onopen = () => setNotice("Live connected");

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.data) {
            setData((old) => ({
              ...old,
              ...msg.data,
              cars: msg.data.cars?.length ? msg.data.cars : old.cars,
              track: msg.data.track?.length ? msg.data.track : old.track,
            }));
          }
        } catch {
          setNotice("Bad socket data");
        }
      };

      ws.onclose = () => {
        setNotice("Reconnecting...");
        retry = setTimeout(connect, 1500);
      };

      ws.onerror = () => setNotice("Socket error");
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

  const progress = Math.max(
    0,
    Math.min(
      100,
      (Number(data.countdown || 0) / Number(data.waiting_seconds || 12)) * 100
    )
  );

  const players = data.players?.length
    ? data.players
    : [
        { avatar: "👨", name: "player_1", balance: "10.00", tag: "WINNER" },
        { avatar: "👩", name: "player_2", balance: "12.50" },
        { avatar: "🧑", name: "player_3", balance: "20.00" },
        { avatar: "👨", name: "player_4", balance: "15.00" },
        { avatar: "👩", name: "player_5", balance: "18.00" },
        { avatar: "🧑", name: "player_6", balance: "30.00" },
      ];

  async function placeBet(carKey) {
    if (data.phase !== "betting") {
      setNotice("Betting closed");
      return;
    }

    try {
      const res = await fetch(`${API}/api/games/lucky-race/bet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "demo_user", bet_type: carKey, amount: Number(chip) }),
      });

      const json = await res.json();
      setNotice(json.message || "Bet placed");
    } catch {
      setNotice("Backend not connected");
    }
  }

  async function clearBets() {
    try {
      const res = await fetch(`${API}/api/games/lucky-race/clear`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "demo_user" }),
      });

      const json = await res.json();
      setNotice(json.message || "Cleared");
    } catch {
      setNotice("Backend not connected");
    }
  }

  return (
    <div className="lr-app">
      <header className="lr-top">
        <a href="/" className="lr-icon-button">‹</a>
        <button className="lr-icon-button" type="button">i</button>

        <div className="lr-title">
          <span>Lucky</span>
          <b>Car Roulette</b>
        </div>

        <button className="lr-add" type="button">
          ADD <span>₹</span>
        </button>
      </header>

      <main className="lr-main">
        <aside className="lr-side lr-left">
          {players.slice(0, 3).map((player, index) => (
            <PlayerCard key={index} player={player} />
          ))}
        </aside>

        <section className="lr-game">
          <div className="lr-track-wrap">
            <LuckyTrackCanvas data={data} progress={progress} />
          </div>

          <div className="lr-status">
            {data.phase === "betting" && "PLACE YOUR BETS"}
            {data.phase === "spinning" && "LUCKY MOVING..."}
            {data.phase === "result" && `WINNER: ${data.winner?.label || ""}`}
          </div>

          <div className="lr-board">
            {(data.cars?.length ? data.cars : FALLBACK_CARS).map((car) => {
              const totals = data.board_totals?.[car.key] || { my: 0, total: 0 };
              const isWinner = data.phase === "result" && data.winner?.key === car.key;
              const myAmount = betMap[car.key] || 0;

              return (
                <button
                  key={car.key}
                  type="button"
                  className={`lr-bet-box ${carClass(car.key)} ${isWinner ? "winner" : ""}`}
                  onClick={() => placeBet(car.key)}
                >
                  <div className="lr-bet-head">
                    <BoardLogo car={car} />
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
          {players.slice(3, 6).map((player, index) => (
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
              type="button"
              className={chip === value ? "active" : ""}
              onClick={() => setChip(value)}
            >
              {value}
            </button>
          ))}
        </div>

        <button className="lr-clear" type="button" onClick={clearBets}>
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

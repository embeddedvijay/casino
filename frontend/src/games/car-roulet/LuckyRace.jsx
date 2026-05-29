import React, { useEffect, useMemo, useState } from "react";
import "./luckyRace.css";

const API = "http://localhost:8005";
const WS = "ws://localhost:8005/ws/lucky-race";
const USER_ID = "demo_user";

const LOGO = "/new-logos/";

const fileName = (name) =>
  name === "land_rover" ? "land_rover.png" : `${name}.png`;

const logos = [
  ["bmw", 22, 7],
  ["ferrari", 28, 7],
  ["jaguar", 34, 7],
  ["lamborghini", 40, 7],
  ["land_rover", 46, 7],
  ["maserati", 54, 7],
  ["star", 50, 7],
  ["mercedes", 60, 7],
  ["porsche", 66, 7],

  ["bmw", 72, 7],
  ["ferrari", 78, 7],
  ["jaguar", 84, 9],
  ["lamborghini", 90, 15],
  ["land_rover", 94, 27],
  ["maserati", 97, 40],
  ["mercedes", 97, 55],
  ["porsche", 95, 70],

  ["bmw", 91, 83],
  ["ferrari", 86, 90],
  ["jaguar", 80, 92],
  ["lamborghini", 74, 93],
  ["land_rover", 68, 93],
  ["maserati", 62, 93],
  ["mercedes", 56, 93],
  ["porsche", 50, 93],

  ["bmw", 44, 93],
  ["ferrari", 38, 93],
  ["jaguar", 32, 93],
  ["lamborghini", 26, 93],
  ["land_rover", 20, 93],
  ["maserati", 14, 90],
  ["mercedes", 9, 83],
  ["porsche", 5, 70],

  ["bmw", 3, 55],
  ["ferrari", 3, 40],
  ["jaguar", 6, 27],
  ["lamborghini", 10, 15],
  ["land_rover", 16, 9],
];

const betCars = [
  "bmw",
  "ferrari",
  "jaguar",
  "lamborghini",
  "land_rover",
  "maserati",
  "mercedes",
  "porsche",
];

const coins = [10, 50, 100, 200, 500, 1000];

export default function LuckyRace() {
  const [gameState, setGameState] = useState(null);
  const [selectedCoin, setSelectedCoin] = useState(10);
  const [activeTab, setActiveTab] = useState("all");
  const [connection, setConnection] = useState("Connecting");

  const [localBets, setLocalBets] = useState(
    Object.fromEntries(betCars.map((car) => [car, "0"]))
  );

  const syncBets = (data) => {
    const next = Object.fromEntries(betCars.map((car) => [car, "0"]));

    if (data?.board_totals) {
      betCars.forEach((car) => {
        const myAmount = data.board_totals?.[car]?.my || 0;
        next[car] = String(myAmount);
      });
    }

    setLocalBets(next);
  };

  useEffect(() => {
    fetch(`${API}/api/games/lucky-race/state`)
      .then((res) => res.json())
      .then((data) => {
        setGameState(data);
        syncBets(data);
      })
      .catch(() => setConnection("Offline"));

    const socket = new WebSocket(WS);

    socket.onopen = () => setConnection("Live connected");

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg?.data) {
        setGameState(msg.data);
        syncBets(msg.data);
      }
    };

    socket.onerror = () => setConnection("Connection error");
    socket.onclose = () => setConnection("Disconnected");

    return () => socket.close();
  }, []);

  const phase = gameState?.phase || "waiting";
  const countdown = gameState?.countdown ?? 0;
  const rawTrackIndex = gameState?.track_index ?? 0;
  const trackIndex = rawTrackIndex % logos.length;

  const history = gameState?.history || [];
  const players = gameState?.players || [];
  const myBets = gameState?.my_bets || [];
  const winner = gameState?.winner || null;

  const activeLogo = logos[trackIndex] || logos[0];

  const totalBet = useMemo(() => {
    return Object.values(localBets).reduce(
      (sum, value) => sum + Number(value || 0),
      0
    );
  }, [localBets]);

  const totalWin = useMemo(() => {
    return myBets.reduce((sum, bet) => sum + Number(bet.payout || 0), 0);
  }, [myBets]);

  const winnerName = winner?.name || winner?.key || "";

  const placeCoinBet = async (car) => {
    if (phase !== "betting") return;

    await fetch(`${API}/api/games/lucky-race/bet`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: USER_ID,
        bet_type: car,
        amount: selectedCoin,
      }),
    });
  };

  const clearBets = async () => {
    await fetch(`${API}/api/games/lucky-race/clear`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: USER_ID }),
    });
  };

  return (
    <div className="cr-page">
      <header className="cr-topbar">
        <div className="cr-brand">
          <span>⌂</span>
          <strong>GOLD365</strong>
        </div>

        <div className="cr-account">
          <span>🌐</span>
          <strong>₹ 0.00</strong>
          <span>☰</span>
          <b>DEMO123</b>
        </div>
      </header>

      <aside className="cr-sidebar">
        <div className="cr-tabs">
          <button
            className={activeTab === "all" ? "active" : ""}
            onClick={() => setActiveTab("all")}
          >
            All Bets
          </button>

          <button
            className={activeTab === "my" ? "active" : ""}
            onClick={() => setActiveTab("my")}
          >
            My Bet
          </button>
        </div>

        <h3>{activeTab === "all" ? "ALL BETS" : "MY BETS"}</h3>

        <p className="cr-count">
          {activeTab === "all" ? players.length : myBets.length}
        </p>

        <div className="cr-bet-head">
          <span>User</span>
          <span>Bet(INR)</span>
          <span>Cash out</span>
        </div>

        <div className="cr-user-list">
          {activeTab === "all"
            ? players.map((user, index) => (
                <div className="cr-user-row" key={index}>
                  <span className="cr-user">
                    <i>{user.avatar || "👤"}</i>
                    {user.name}
                  </span>

                  <strong>{Number(user.balance || 0).toFixed(2)}</strong>
                  <strong>{user.tag || "0.00"}</strong>
                </div>
              ))
            : myBets.map((bet) => (
                <div className="cr-user-row" key={bet.id}>
                  <span className="cr-user">
                    <i>🚗</i>
                    {bet.bet_type}
                  </span>

                  <strong>{Number(bet.amount || 0).toFixed(2)}</strong>
                  <strong>{Number(bet.payout || 0).toFixed(2)}</strong>
                </div>
              ))}
        </div>
      </aside>

      <main className="cr-main">
        <div className="cr-round-row">
          <div className="cr-result-panel">
            <span className="cr-result-title">LAST RESULT</span>

            <div className="cr-result-logos">
              {history.length === 0 && (
                <span className="cr-empty">No Result</span>
              )}

              {history
                .slice(-8)
                .reverse()
                .map((item) => (
                  <div className="cr-result-logo" key={item.round_id}>
                    <img
                      src={`${LOGO}${fileName(item.winner?.key)}`}
                      alt={item.winner?.key}
                    />
                  </div>
                ))}
            </div>
          </div>

          <div className={`cr-round-info ${phase}`}>
            <span>{phase.toUpperCase()}</span>
            <strong>{countdown}s</strong>
          </div>
        </div>

        <div className="cr-table">
          <div className="cr-outer">
            {logos.map(([logo, x, y], i) => (
              <div
                key={`${logo}-${i}`}
                className={`cr-logo ${
                  trackIndex === i ? "cr-logo-active" : ""
                }`}
                style={{ left: `${x}%`, top: `${y}%` }}
              >
                <img src={`${LOGO}${fileName(logo)}`} alt={logo} />
              </div>
            ))}

            <div
              className="cr-moving-marker"
              style={{
                left: `${activeLogo[1]}%`,
                top: `${activeLogo[2]}%`,
              }}
            >
              <img src={`${LOGO}${fileName(activeLogo[0])}`} alt="" />
            </div>

            <div className="cr-betting-grid">
              {betCars.map((car) => (
                <div
                  className="cr-bet-cell"
                  key={car}
                  onClick={() => placeCoinBet(car)}
                >
                  <span className="cr-rupee">₹</span>

                  <div className="cr-input-strip">
                    <input
                      type="text"
                      inputMode="numeric"
                      value={localBets[car] || "0"}
                      readOnly
                    />
                  </div>

                  <img
                    className="cr-bet-logo"
                    src={`${LOGO}${fileName(car)}`}
                    alt={car}
                  />
                </div>
              ))}
            </div>

            {phase === "result" && winner && (
              <div className="cr-winner-popup">
                <span>WINNER</span>

                <img
                  src={`${LOGO}${fileName(winner.key)}`}
                  alt={winner.key}
                />
              </div>
            )}
          </div>
        </div>

        <div className="cr-coin-panel">
          {coins.map((coin) => (
            <button
              key={coin}
              className={`cr-coin ${selectedCoin === coin ? "active" : ""}`}
              onClick={() => setSelectedCoin(coin)}
            >
              ₹{coin}
            </button>
          ))}

          <button className="cr-clear-btn" onClick={clearBets}>
            CLEAR
          </button>
        </div>
      </main>

      {phase === "result" && winner && (
        <div className="cr-win-effect">
          <div className="cr-win-backdrop" />
          <div className="cr-firework cr-firework-one" />
          <div className="cr-firework cr-firework-two" />
          <div className="cr-firework cr-firework-three" />

          <div className="cr-win-rays" />

          <div className="cr-winner-mega-card">
            <div className="cr-win-crown">♛</div>
            <h1>WINNER</h1>

            <div className="cr-win-logo-ring">
              <img src={`${LOGO}${fileName(winner.key)}`} alt={winner.key} />
            </div>

            <h2>{winnerName}</h2>
            <p>YOU WIN</p>

            <strong>₹ {totalWin.toFixed(2)}</strong>
          </div>

          <div className="cr-collect-glow">COLLECT WINNINGS</div>

          {Array.from({ length: 32 }).map((_, index) => (
            <span key={index} className={`cr-falling-coin coin-${index}`}>
              ₹
            </span>
          ))}
        </div>
      )}

      <div className="cr-live-box">
        <span>{connection}</span>
        <strong>Total bets: {totalBet.toFixed(2)}</strong>
      </div>
    </div>
  );
}
import React, { useEffect, useMemo, useState } from "react";
import "./luckyRace.css";

// const API = "http://localhost:8005";
// const WS = "ws://localhost:8005/ws/lucky-race";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;
const WS=`ws://${HOST}:8005/ws/lucky-race`;

const USER_ID = "demo_user";
const LOGO = "/new-logos/";

const fileName = (name) =>
  name === "land_rover" ? "land_rover.png" : `${name}.png`;

const logos = [
  ["bmw", 27, 10],
  ["ferrari", 36, 10],
  ["jaguar", 45, 10],
  ["lamborghini", 53, 10],
  ["land_rover", 62, 10],
  ["maserati", 70, 10],
  ["mercedes", 80, 10],
  ["porsche", 87, 14],

  ["bmw", 93, 25],
  ["ferrari", 96, 42],
  ["jaguar", 96, 59],
  ["lamborghini", 93, 75],
  ["land_rover", 87, 85],
  ["maserati", 80, 88],
  ["mercedes", 71, 88],
  ["porsche", 62, 88],

  ["bmw", 53, 88],
  ["ferrari", 44, 88],
  ["jaguar", 35, 88],
  ["lamborghini", 27, 88],
  ["land_rover", 18, 88],
  ["maserati", 11, 82],
  ["mercedes", 6, 70],
  ["porsche", 4, 55],
  
  ["bmw", 4, 40],
  ["ferrari", 6, 25],
  ["jaguar", 12, 16],
  ["lamborghini", 19, 10],
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

function money(value) {
  return Number(value || 0).toFixed(2);
}

function prettyName(name = "") {
  return String(name).replace("_", " ").toUpperCase();
}

function trackShortName(name = "") {
  return prettyName(name).replace("LAMBORGHINI", "LAMBO").replace("LAND ROVER", "LAND ROVER");
}

function CarLogo({ name, className = "" }) {
  if (!name) return null;

  return (
    <img
      className={className}
      src={`${LOGO}${fileName(name)}`}
      alt={name}
      draggable="false"
    />
  );
}

function TopBar({ totalBet, totalWin, roundId, phase, countdown }) {
  return (
    <header className="cr-topbar">
      <div className="cr-brand">
        <span className="cr-brand-badge">♛</span>
        <strong>GOLD365</strong>
      </div>

      <section className="cr-top-stats">
        <div className="cr-stat-card">
          <span>💰 Total Bet</span>
          <b>₹ {money(totalBet)}</b>
        </div>
        <div className="cr-stat-card">
          <span>🏆 Last Win</span>
          <b>₹ {money(totalWin)}</b>
        </div>
        <div className="cr-stat-card">
          <span>▣ Round ID</span>
          <b>{roundId || "-"}</b>
        </div>
        <div className="cr-stat-card">
          <span>● Status</span>
          <b>{phase}</b>
        </div>
        <div className="cr-stat-card countdown">
          <span>⏱ Countdown</span>
          <b>{String(countdown || 0).padStart(2, "0")}</b>
        </div>
      </section>

      <div className="cr-account">
        <div className="cr-wallet">💼 ₹ 0.00</div>
        <button className="cr-plus">+</button>
        <b>DEMO123</b>
        <span className="cr-user-dot">●</span>
      </div>
    </header>
  );
}

function Sidebar({ activeTab, setActiveTab, players, myBets }) {
  const topPlayer = players[0];

  return (
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
                <strong>₹ {money(user.balance)}</strong>
                <strong className={user.tag === "WINNER" ? "winner" : ""}>
                  {user.tag || "0.00"}
                </strong>
              </div>
            ))
          : myBets.map((bet) => (
              <div className="cr-user-row" key={bet.id}>
                <span className="cr-user">
                  <i>🚗</i>
                  {prettyName(bet.bet_type)}
                </span>
                <strong>₹ {money(bet.amount)}</strong>
                <strong>₹ {money(bet.payout)}</strong>
              </div>
            ))}
      </div>

      <div className="cr-jackpot-card">
        <span>JACKPOT</span>
        <b>₹ 1,25,000</b>
      </div>

      <div className="cr-top-winner">
        <i>👑</i>
        <div>
          <span>TOP WINNER</span>
          <b>{topPlayer?.name || "Raj Banna Saa"}</b>
          <strong>₹ {money(topPlayer?.balance || 95680)}</strong>
        </div>
      </div>
    </aside>
  );
}


function RightPanel({ players }) {
  const topPlayer = players[0];
  return (
    <aside className="cr-right-panel">
      <div className="cr-daily-jackpot">
        <span>DAILY JACKPOT</span>
        <i>🏆</i>
        <b>₹ 1,25,000</b>
      </div>
      <div className="cr-last-winner-card">
        <span>LAST WINNER</span>
        <div className="cr-last-car">🏎️</div>
        <b>{topPlayer?.name || "Raj Banna Saa"}</b>
        <strong>₹ {money(topPlayer?.balance || 42569)}</strong>
      </div>
    </aside>
  );
}

function ResultStrip({ history }) {
  return (
    <section className="cr-result-panel">
      <span className="cr-result-title">LAST RESULT</span>

      <div className="cr-result-logos">
        {history.length === 0 && <span className="cr-empty">No Result</span>}

        {history
          .slice(-27)
          .reverse()
          .map((item) => (
            <div className="cr-result-logo" key={item.round_id}>
              <CarLogo name={item.winner?.key} />
            </div>
          ))}
      </div>
    </section>
  );
}

function RaceBoard({ logos, trackIndex, activeLogo, betCars, localBets, placeCoinBet, phase, winner }) {
  return (
    <div className="cr-table">
      <div className="cr-outer">
        <div className="cr-track-glow" />

        {logos.map(([logo, x, y], i) => (
          <div
            key={`${logo}-${i}`}
            className={`cr-logo ${trackIndex === i ? "cr-logo-active" : ""}`}
            style={{ left: `${x}%`, top: `${y}%` }}
          >
            {/* <span className="cr-track-no">{String(i + 1).padStart(2, "0")}</span> */}
            <CarLogo name={logo} />
            {/* <span className="cr-track-name">{trackShortName(logo)}</span> */}
          </div>
        ))}

        <div
          className={`cr-moving-marker ${phase==="stopping"?"stop-effect":""}`}
          style={{
            left: `${activeLogo[1]}%`,
            top: `${activeLogo[2]}%`,
          }}
        >
          <CarLogo name={activeLogo[0]} />
        </div>

        {phase === "result" && winner && (
          <div className="cr-winner-popup">
            <span>WINNER</span>
            <CarLogo name={winner.key} />
          </div>
        )}
      </div>
    </div>
  );
}


function BettingBoard({ betCars, localBets, placeCoinBet }) {
  return (
    <div className="cr-betting-grid cr-betting-grid-under">
      {betCars.map((car) => (
        <button
          className="cr-bet-cell"
          key={car}
          onClick={() => placeCoinBet(car)}
        >
          <CarLogo name={car} className="cr-bet-logo" />
          <span className="cr-bet-name">{prettyName(car)}</span>
          <span className="cr-odds">x8.0</span>
          <span className="cr-rupee">₹ {localBets[car] || "0"}</span>
        </button>
      ))}
    </div>
  );
}

function FeatureCards() {
  return (
    <section className="cr-feature-cards">
      <div>
        <i>🛡</i>
        <b>FAIR PLAY</b>
        <span>100% Secure & Fair</span>
      </div>
      <div>
        <i>🎧</i>
        <b>24/7 SUPPORT</b>
        <span>We are always here</span>
      </div>
      <div>
        <i>⚡</i>
        <b>FAST PAYOUTS</b>
        <span>Instant Withdrawals</span>
      </div>
      <div>
        <i>🏆</i>
        <b>BEST ODDS</b>
        <span>High Winning Chance</span>
      </div>
    </section>
  );
}

function CoinPanel({ coins, selectedCoin, setSelectedCoin, clearBets }) {
  return (
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
        ↻<span>CLEAR</span>
      </button>

      <button className="cr-bet-submit">
        BET <span>➤</span>
      </button>
    </div>
  );
}

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
  const serverTrackLength = 28;
  const trackIndex = rawTrackIndex % serverTrackLength;

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
      <TopBar
        totalBet={totalBet}
        totalWin={totalWin}
        roundId={gameState?.round_id}
        phase={phase}
        countdown={countdown}
      />

      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        players={players}
        myBets={myBets}
      />

      <RightPanel players={players} />

      <main className="cr-main">
        <div className="cr-round-row">
          <ResultStrip history={history} />

          <div className={`cr-round-info ${phase}`}>
            <span>BETTING TIME</span>
            <strong>{String(countdown || 0).padStart(2, "0")}s</strong>
          </div>
        </div>

        <RaceBoard
          logos={logos}
          trackIndex={trackIndex}
          activeLogo={activeLogo}
          betCars={betCars}
          localBets={localBets}
          placeCoinBet={placeCoinBet}
          phase={phase}
          winner={winner}
        />

        <BettingBoard
          betCars={betCars}
          localBets={localBets}
          placeCoinBet={placeCoinBet}
        />

        <CoinPanel
          coins={coins}
          selectedCoin={selectedCoin}
          setSelectedCoin={setSelectedCoin}
          clearBets={clearBets}
        />

        <FeatureCards />
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
              <CarLogo name={winner.key} />
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
        <span><i /> {connection}</span>
        <strong>Total bets: ₹ {totalBet.toFixed(2)}</strong>
      </div>
    </div>
  );
}
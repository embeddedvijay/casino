import React, { useEffect, useState } from "react";
import "./matkaDashboard.css";

const API = "http://localhost:8005";

const games = [
  { key: "SRIDEVI_DAY", name: "SRIDEVI DAY", type: "day" },
  { key: "SRIDEVI_NIGHT", name: "SRIDEVI NIGHT", type: "night" },

  { key: "TIME_BAZAR_DAY", name: "TIME BAZAR", type: "day" },
  { key: "MAIN_BAZAR_NIGHT", name: "MAIN BAZAR", type: "night" },

  { key: "MADHUR_DAY", name: "MADHUR DAY", type: "day" },
  { key: "MADHUR_NIGHT", name: "MADHUR NIGHT", type: "night" },

  { key: "MILAN_DAY", name: "MILAN DAY", type: "day" },
  { key: "MILAN_NIGHT", name: "MILAN NIGHT", type: "night" },

  { key: "RAJDHANI_DAY", name: "RAJDHANI DAY", type: "day" },
  { key: "RAJDHANI_NIGHT", name: "RAJDHANI NIGHT", type: "night" },
  
  { key: "SUPREME_DAY", name: "SUPREME DAY", type: "day" },
  { key: "SUPREME_NIGHT", name: "SUPREME NIGHT", type: "night" },

  { key: "KALYAN_DAY", name: "KALYAN DAY", type: "day" },
  { key: "KALYAN_NIGHT", name: "KALYAN NIGHT", type: "night" },
];

const possibleKeys = (key) => {
  const base = key.replace("_OP", "").replace("_CL", "");

  return [
    key,
    `${base}_OP`,
    `${base}_CL`,
    base,
    base.replace("_DAY", ""),
    base.replace("_NIGHT", ""),
  ];
};

const getMarket = (results, key) => {
  if (!results) return null;

  for (const k of possibleKeys(key)) {
    if (results[k]) return results[k];
  }

  return null;
};

const safe = (value, fallback = "*") => {
  if (value === undefined || value === null || value === "") return fallback;
  return String(value);
};

const splitPana = (value) => {
  return safe(value, "***").padEnd(3, "*").slice(0, 3).split("");
};

const getValue = (market, keys, fallback = "*") => {
  if (!market) return fallback;

  for (const key of keys) {
    if (market[key] !== undefined && market[key] !== null && market[key] !== "") {
      return String(market[key]);
    }
  }

  return fallback;
};

function ResultCard({ game, market }) {
  const open = getValue(market, ["OPEN", "open"], "*");
  const close = getValue(market, ["CLOSE", "close"], "*");

  const opana = getValue(
    market,
    ["OPANAL", "OPANA", "OPENPANA", "openPana", "open_pana"],
    "***"
  );

  const cpana = getValue(
    market,
    ["CPANAL", "CPANA", "CLOSEPANA", "closePana", "close_pana"],
    "***"
  );

  const openTime = getValue(
    market,
    ["OTIME", "openTime", "open_time"],
    "--:--:--"
  );

  const closeTime = getValue(
    market,
    ["CTIME", "closeTime", "close_time"],
    "--:--:--"
  );

  const result = `${open}${close}`;

  return (
    <div className={`mk-card ${game.type === "day" ? "mk-card-orange" : "mk-card-blue"}`}>
      <h2>{game.name}</h2>

      <div className="mk-stars">★★★★★</div>

      <div className="mk-ribbon">Daily</div>

      <div className="mk-time-row">
        <span>{openTime}</span>
        <span>{closeTime}</span>
      </div>

      <div className="mk-result-row">
        <div>
          {splitPana(opana).map((n, i) => (
            <b key={i}>{n}</b>
          ))}
        </div>

        <strong>{result === "**" ? "**" : result}</strong>

        <div>
          {splitPana(cpana).map((n, i) => (
            <b key={i}>{n}</b>
          ))}
        </div>
      </div>

      <button className="mk-play-btn">▶ PLAY NOW</button>
    </div>
  );
}

export default function MatkaDashboard() {
  const [resultDoc, setResultDoc] = useState(null);
  const [status, setStatus] = useState("Loading");

  useEffect(() => {
    const loadResults = () => {
      fetch(`${API}/api/games/matka/results/latest`)
        .then((res) => res.json())
        .then((data) => {
          console.log("MATKA RESULT API:", data);
          setResultDoc(data);
          setStatus("Live Result");
        })
        .catch((err) => {
          console.error("MATKA API ERROR:", err);
          setResultDoc(null);
          setStatus("API Error");
        });
    };

    loadResults();

    const interval = setInterval(loadResults, 10000);

    return () => clearInterval(interval);
  }, []);

  const results =
  resultDoc?.Result && typeof resultDoc.Result === "object"
    ? resultDoc.Result
    : resultDoc || {};
  const mainBazar = getMarket(results, "MAIN_BAZAR_NIGHT");

  const mainText = mainBazar
    ? `${getValue(mainBazar, ["OPANAL", "OPANA"], "***")} - ${getValue(mainBazar, ["OPEN"], "*")}${getValue(mainBazar, ["CLOSE"], "*")} - ${getValue(mainBazar, ["CPANAL", "CPANA"], "***")}`
    : "*** - ** - ***";

  return (
    <div className="mk-page">
      <header className="mk-top">
        <div className="mk-menu">☰</div>

        <div className="mk-logo">
          <span>♛</span>
          <b>MatkaBooking</b>
          <em>{status}</em>
        </div>

        <div className="mk-main-bazar">
          <small>MAIN BAZAR</small>
          <strong>{mainText}</strong>
        </div>

        <div className="mk-wallet">
          <span>🪙</span>
          <b>₹ 12,580.50</b>
          <button>+</button>
        </div>

        <div className="mk-user">
          <span>👤</span>
          <div>
            <b>Rahul Jha</b>
            <small>ID: 5689</small>
          </div>
          <i>⌄</i>
        </div>
      </header>

      <nav className="mk-nav">
        <button className="active">⌂ Home</button>
        <button>🏆 Results</button>
        <button>▶ Play Game</button>
        <button>▣ My Bids</button>
        <button>💳 Add Money</button>
        <button>🏦 Withdraw</button>
        <button>◷ History</button>
        <button>👤 Profile</button>
        <button>🎧 Support</button>
      </nav>

      <main className="mk-content">
        <div className="mk-grid">
          {games.map((game, index) => (
            <ResultCard
              key={index}
              game={game}
              market={getMarket(results, game.key)}
            />
          ))}
        </div>
      </main>
    </div>
  );
}
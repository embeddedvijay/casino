import React, { useEffect, useState } from "react";
import "./matkaDashboard.css";

const API = "http://localhost:8005";

const games = [
  { key: "SRIDEVI_DAY", name: "SRIDEVI DAY", type: "day", art: "lakshmi", tone: "gold" },
  { key: "SRIDEVI_NIGHT", name: "SRIDEVI NIGHT", type: "night", art: "lotus", tone: "blue" },
  { key: "TIME_BAZAR_DAY", name: "TIME BAZAR", type: "day", art: "hourglass", tone: "gold" },
  { key: "MAIN_BAZAR_NIGHT", name: "MAIN BAZAR", type: "night", art: "temple", tone: "purple" },
  { key: "MADHUR_DAY", name: "MADHUR DAY", type: "day", art: "laddu", tone: "gold" },
  { key: "MADHUR_NIGHT", name: "MADHUR NIGHT", type: "night", art: "moon", tone: "blue" },
  { key: "MILAN_DAY", name: "MILAN DAY", type: "day", art: "kalash", tone: "gold" },
  { key: "MILAN_NIGHT", name: "MILAN NIGHT", type: "night", art: "diya", tone: "blue" },
  { key: "RAJDHANI_DAY", name: "RAJDHANI DAY", type: "day", art: "gate", tone: "purple" },
  { key: "RAJDHANI_NIGHT", name: "RAJDHANI NIGHT", type: "night", art: "stars", tone: "blue" },
  { key: "SUPREME_DAY", name: "SUPREME DAY", type: "day", art: "crown", tone: "gold" },
  { key: "SUPREME_NIGHT", name: "SUPREME NIGHT", type: "night", art: "lotus", tone: "blue" },
  { key: "KALYAN_DAY", name: "KALYAN DAY", type: "day", art: "coins", tone: "gold" },
  { key: "KALYAN_NIGHT", name: "KALYAN NIGHT", type: "night", art: "moon", tone: "blue" },
];

const artIcon = {
  lakshmi: "🪷",
  lotus: "🪷",
  hourglass: "⏳",
  temple: "🛕",
  laddu: "🟡",
  moon: "🌙",
  kalash: "🏺",
  diya: "🪔",
  gate: "🏛️",
  stars: "✨",
  crown: "👑",
  coins: "🪙",
};

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
    <article className={`mk-card mk-card-${game.tone}`}>
      <div className="mk-card-glow" />
      <div className={`mk-card-art mk-art-${game.art}`}>
        <span>{artIcon[game.art]}</span>
      </div>

      <div className="mk-card-content">
        <h2>{game.name}</h2>
        <div className="mk-stars">★★★★★</div>

        <div className="mk-time-row">
          <span><i>⏱</i>{openTime}</span>
          <span><i>⏱</i>{closeTime}</span>
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
    </article>
  );
}

function TrustFooter() {
  return (
    <section className="mk-trust-row">
      <div><span>🛡</span><b>100% SECURE</b><small>Your money is safe</small></div>
      <div><span>🏆</span><b>FAIR PLAY</b><small>We ensure fair gaming</small></div>
      <div><span>⚡</span><b>FAST WITHDRAWAL</b><small>Withdraw in 24hrs</small></div>
      <div><span>🎧</span><b>24/7 SUPPORT</b><small>We are here for you</small></div>
    </section>
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
        </div>

        <div className="mk-main-bazar">
          <small>✨ MAIN BAZAR ✨</small>
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

      <main className="mk-content">
        <aside className="mk-side-panel mk-side-left">
          <div className="mk-hanging-lamps">🪔</div>
          <h3>किस्मत<br />आपकी<br />साथ हमारा</h3>
          <div className="mk-pot">🏺</div>
          <div className="mk-balls"><span>5</span><span>6</span></div>
        </aside>

        <section className="mk-center">
          <div className="mk-status-pill">{status}</div>
          <div className="mk-grid">
            {games.map((game, index) => (
              <ResultCard
                key={index}
                game={game}
                market={getMarket(results, game.key)}
              />
            ))}
          </div>
          <TrustFooter />
        </section>

        <aside className="mk-side-panel mk-side-right">
          <div className="mk-hanging-lamps">🪔</div>
          <h3>खेलो और<br />जीतो!</h3>
          <div className="mk-pot">🏺</div>
          <div className="mk-balls"><span>3</span><span>9</span></div>
        </aside>
      </main>
    </div>
  );
}

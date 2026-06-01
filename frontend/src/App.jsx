import React from "react";
import Aviator from "./games/aviator/Aviator.jsx";
import DragonTiger from "./games/dragon-tiger/DragonTiger.jsx";
import LuckyRace from "./games/car-roulet/LuckyRace.jsx";
import MatkaDashboard from "./games/matka/MatkaDashboard.jsx";
import MarketInput from "./games/matka/MarketInput.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import CreateAccount from "./pages/CreateAccount.jsx";
import ForgotPassword from "./pages/ForgotPassword.jsx";

const lobbyGames = [
  { path: "/aviator", tag: "HOT", theme: "#ff0b58", image: "/casino-assets/aviator.png" },
  { path: "/dragon-tiger", tag: "POPULAR", theme: "#ffc400", image: "/casino-assets/dragon-tiger.png" },
  { path: "/lucky-race", tag: "NEW", theme: "#a855ff", image: "/casino-assets/lucky-race.png" },
  { path: "/matka", tag: "CLASSIC", theme: "#b000ff", image: "/casino-assets/matka.png" },
];

function GameLobby() {
  return (
    <div style={styles.page}>
      <style>
        {`
          @keyframes bgZoom {
            0% { transform: scale(1); }
            50% { transform: scale(1.06); }
            100% { transform: scale(1); }
          }

          @keyframes lightMove {
            0% { transform: translateX(-130%); opacity: 0; }
            35% { opacity: .45; }
            100% { transform: translateX(130%); opacity: 0; }
          }

          @keyframes floatGlow {
            0%, 100% { transform: translateY(0); opacity: .45; }
            50% { transform: translateY(-18px); opacity: .85; }
          }

          .casino-bg-anim {
            animation: bgZoom 18s ease-in-out infinite;
          }

          .casino-light-sweep {
            animation: lightMove 7s linear infinite;
          }

          .casino-float-glow {
            animation: floatGlow 4s ease-in-out infinite;
          }
        `}
      </style>

      <div style={styles.animatedBg} className="casino-bg-anim" />
      <div style={styles.overlay} />
      <div style={styles.lightSweep} className="casino-light-sweep" />
      <div style={styles.floatGlowOne} className="casino-float-glow" />
      <div style={styles.floatGlowTwo} className="casino-float-glow" />

      <header style={styles.header}>
        <div style={styles.logoBox}>
          <div style={styles.brand}>
            <span style={styles.crown}>♛</span>
            <strong>
              GOLD<span>365</span>
            </strong>
          </div>
          <p style={styles.brandSub}>PLAY · WIN · REPEAT</p>
        </div>
      </header>

      <section style={styles.cards}>
        {lobbyGames.map((game) => (
          <a
            href={`/login?redirect=${encodeURIComponent(game.path)}`}
            key={game.path}
            style={{
              ...styles.card,
              borderColor: game.theme,
              boxShadow: `0 0 26px ${game.theme}66`,
            }}
          >
            <div style={{ ...styles.ribbon, background: game.theme }}>
              {game.tag}
            </div>

            <div
              style={{
                ...styles.visual,
                backgroundImage: `url(${game.image})`,
              }}
            />

            <button
              style={{
                ...styles.playBtn,
                borderColor: game.theme,
                boxShadow: `0 0 18px ${game.theme}88`,
              }}
            >
              PLAY NOW ›
            </button>
          </a>
        ))}
      </section>

      <footer style={styles.footer}>
        <div style={styles.footerItem}>
          <span>🛡️</span>
          <strong>100% SECURE</strong>
        </div>
        <div style={styles.footerItem}>
          <span>🎧</span>
          <strong>24/7 SUPPORT</strong>
        </div>
        <div style={styles.footerItem}>
          <span>🏆</span>
          <strong>FAIR PLAY</strong>
        </div>
        <div style={styles.footerItem}>
          <span>🎁</span>
          <strong>DAILY BONUS</strong>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  const path = window.location.pathname;

  if (path === "/aviator") return <Aviator />;
  if (path === "/dragon-tiger") return <DragonTiger />;
  if (path === "/lucky-race") return <LuckyRace />;
  if (path === "/matka") return <MatkaDashboard />;
  if (path === "/login") return <LoginPage />;
  if (path === "/create-account") return <CreateAccount />;
  if (path === "/forgot-password") return <ForgotPassword />;
  if (path.startsWith("/matka/market-input/")) { const marketName=decodeURIComponent(path.split("/matka/market-input/")[1]||""); window.history.replaceState({marketName}, "", "/matka/market-input"); return <MarketInput marketName={marketName}/>; }
  if (path === "/matka/market-input") return <MarketInput marketName={window.history.state?.marketName||""}/>;

  return <GameLobby />;
}

const styles = {
  page: {
    minHeight: "100vh",
    position: "relative",
    overflow: "hidden",
    color: "#fff",
    fontFamily: "Arial, sans-serif",
    padding: "26px 48px 34px",
    background: "#050505",
  },

  animatedBg: {
    position: "absolute",
    inset: "-35px",
    backgroundImage: "url('/casino-assets/casino-bg.png')",
    backgroundSize: "cover",
    backgroundPosition: "center top",
    backgroundRepeat: "no-repeat",
    zIndex: 0,
  },

  overlay: {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    zIndex: 1,
    background:
      "linear-gradient(180deg, rgba(0,0,0,.02) 0%, rgba(0,0,0,.16) 45%, rgba(0,0,0,.74) 100%)",
  },

  lightSweep: {
    position: "absolute",
    top: 0,
    bottom: 0,
    left: 0,
    width: "45%",
    background:
      "linear-gradient(90deg, transparent, rgba(255,214,92,.18), transparent)",
    zIndex: 2,
    pointerEvents: "none",
  },

  floatGlowOne: {
    position: "absolute",
    left: "8%",
    top: "20%",
    width: 180,
    height: 180,
    borderRadius: "50%",
    background: "rgba(255,196,0,.18)",
    filter: "blur(55px)",
    zIndex: 1,
  },

  floatGlowTwo: {
    position: "absolute",
    right: "8%",
    top: "26%",
    width: 210,
    height: 210,
    borderRadius: "50%",
    background: "rgba(176,0,255,.18)",
    filter: "blur(60px)",
    zIndex: 1,
  },

  header: {
    position: "relative",
    zIndex: 5,
    display: "flex",
    justifyContent: "flex-end",
    alignItems: "center",
  },

  logoBox: {
    textAlign: "right",
    background: "rgba(0,0,0,.38)",
    border: "1px solid rgba(255,214,92,.35)",
    borderRadius: 18,
    padding: "10px 18px 8px",
    backdropFilter: "blur(7px)",
  },

  brand: {
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-end",
    gap: 10,
    color: "#ffd65c",
    fontSize: 36,
    fontWeight: 1000,
    textShadow: "0 0 18px rgba(255,214,92,.65)",
    lineHeight: 1,
  },

  crown: {
    fontSize: 44,
  },

  brandSub: {
    margin: "6px 0 0",
    color: "#f7d36a",
    letterSpacing: 4,
    fontWeight: 700,
    fontSize: 12,
  },

  cards: {
    position: "relative",
    zIndex: 5,
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 28,
    marginTop: 145,
  },

  card: {
    position: "relative",
    minHeight: 430,
    border: "2px solid",
    borderRadius: 24,
    overflow: "hidden",
    padding: 18,
    textDecoration: "none",
    color: "#fff",
    background:
      "linear-gradient(180deg, rgba(255,255,255,.06), rgba(0,0,0,.48))",
    backdropFilter: "blur(4px)",
  },

  ribbon: {
    position: "absolute",
    top: 22,
    left: -42,
    transform: "rotate(-45deg)",
    width: 165,
    textAlign: "center",
    padding: "8px 0",
    fontWeight: 1000,
    fontSize: 17,
    zIndex: 3,
  },

  visual: {
    height: 282,
    width: "100%",
    borderRadius: 18,
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    boxShadow: "inset 0 -45px 70px rgba(0,0,0,.45)",
    marginBottom: 14,
  },

  playBtn: {
    position: "absolute",
    left: 32,
    right: 32,
    bottom: 26,
    height: 58,
    borderRadius: 18,
    border: "2px solid",
    background: "rgba(0,0,0,.50)",
    color: "#fff",
    fontSize: 23,
    fontWeight: 1000,
    cursor: "pointer",
  },

  footer: {
    position: "relative",
    zIndex: 5,
    maxWidth: 1400,
    margin: "34px auto 0",
    minHeight: 88,
    borderRadius: 26,
    background: "rgba(0,0,0,.56)",
    border: "1px solid rgba(255,255,255,.16)",
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    alignItems: "center",
    padding: "0 34px",
    backdropFilter: "blur(8px)",
  },

  footerItem: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    color: "#fff",
  },
};
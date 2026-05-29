import React from "react";
import Aviator from "./games/aviator/Aviator.jsx";
import DragonTiger from "./games/dragon-tiger/DragonTiger.jsx";
import LuckyRace from "./games/car-roulet/LuckyRace.jsx";
import MatkaDashboard from "./games/matka/MatkaDashboard.jsx";

const lobbyGames = [
  { path: "/aviator", tag: "HOT", title: "Aviator", theme: "#ff0b58", image: "/casino-assets/aviator.png" },
  { path: "/dragon-tiger", tag: "POPULAR", title: "Dragon Tiger", theme: "#ffc400", image: "/casino-assets/dragon-tiger.png" },
  { path: "/lucky-race", tag: "NEW", title: "Lucky Race", theme: "#a855ff", image: "/casino-assets/lucky-race.png" },
  { path: "/matka", tag: "CLASSIC", title: "Matka", theme: "#b000ff", image: "/casino-assets/matka.png" },
];

function GameLobby() {
  return (
    <div style={styles.page}>
      <div style={styles.overlay} />

      <header style={styles.header}>
        <div style={styles.logoBox}>
          <div style={styles.brand}>
            <span style={styles.crown}>♛</span>
            <strong>GOLD<span>365</span></strong>
          </div>
          <p style={styles.brandSub}>PLAY · WIN · REPEAT</p>
        </div>
      </header>

      <section style={styles.cards}>
        {lobbyGames.map((game) => (
          <a
            href={game.path}
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

            <h2 style={{ color: game.theme }}>{game.title}</h2>

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
        <div style={styles.footerItem}><span>🛡️</span><strong>100% SECURE</strong><small>Safe & Trusted</small></div>
        <div style={styles.footerItem}><span>🎧</span><strong>24/7 SUPPORT</strong><small>We are here</small></div>
        <div style={styles.footerItem}><span>🏆</span><strong>FAIR PLAY</strong><small>Play Fair, Win Big</small></div>
        <div style={styles.footerItem}><span>🎁</span><strong>DAILY BONUS</strong><small>Win More Every Day</small></div>
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
    backgroundImage:
      "linear-gradient(rgba(0,0,0,.08), rgba(0,0,0,.48)), url('/casino-assets/casino-bg.png')",
    backgroundSize: "cover",
    backgroundPosition: "center top",
    backgroundRepeat: "no-repeat",
  },

  overlay: {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background:
      "linear-gradient(180deg, rgba(0,0,0,.02) 0%, rgba(0,0,0,.18) 45%, rgba(0,0,0,.74) 100%)",
  },

  header: {
    position: "relative",
    zIndex: 2,
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
    zIndex: 2,
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
    background: "linear-gradient(180deg, rgba(255,255,255,.06), rgba(0,0,0,.48))",
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
    zIndex: 2,
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
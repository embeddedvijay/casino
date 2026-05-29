import React from "react";
import Aviator from "./games/aviator/Aviator.jsx";
import DragonTiger from "./games/dragon-tiger/DragonTiger.jsx";
import LuckyRace from "./games/car-roulet/LuckyRace.jsx";
import MatkaDashboard from "./games/matka/MatkaDashboard.jsx";

const lobbyGames = [
  {
    path: "/aviator",
    tag: "HOT",
    title: "Aviator",
    theme: "#ff0b58",
    image: "/casino-assets/aviator.png",
  },
  {
    path: "/dragon-tiger",
    tag: "POPULAR",
    title: "Dragon Tiger",
    theme: "#ffc400",
    image: "/casino-assets/dragon-tiger.png",
  },
  {
    path: "/lucky-race",
    tag: "NEW",
    title: "Lucky Race",
    theme: "#a855ff",
    image: "/casino-assets/lucky-race.png",
  },
  {
    path: "/matka",
    tag: "CLASSIC",
    title: "Matka",
    theme: "#b000ff",
    image: "/casino-assets/matka.png",
  },
];

function GameLobby() {
  return (
    <div style={styles.page}>
      <div style={styles.overlay} />

      <header style={styles.header}>


        <div style={styles.topRight}>
        <div>
          <div style={styles.brand}>
            <span style={styles.crown}>♛</span>
            <strong>
              GOLD<span>365</span>
            </strong>
          </div>
          <p style={styles.brandSub}>PLAY · WIN · REPEAT</p>
        </div>
        </div>
      </header>

      <section style={styles.hero}>
        <div style={styles.goldLine}></div>
      </section>

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
            <div
              style={{
                ...styles.ribbon,
                background: game.theme,
              }}
            >
              {game.tag}
            </div>

            <div
              style={{
                ...styles.visual,
                backgroundImage: `url(${game.image})`,
              }}
            />

            <h2 style={{ color: game.theme }}>{game.title}</h2>
            <p>{game.subtitle}</p>

            <button
              style={{
                ...styles.playBtn,
                borderColor: game.theme,
                boxShadow: `0 0 18px ${game.theme}88`,
              }}
            >
              PLAY NOW <span>›</span>
            </button>
          </a>
        ))}
      </section>

      <footer style={styles.footer}>
        <div style={styles.footerItem}>
          <span>🛡️</span>
          <div>
            <strong>100% SECURE</strong>
            <small>Safe & Trusted</small>
          </div>
        </div>

        <div style={styles.footerItem}>
          <span>🎧</span>
          <div>
            <strong>24/7 SUPPORT</strong>
            <small>We are here</small>
          </div>
        </div>

        <div style={styles.footerItem}>
          <span>🏆</span>
          <div>
            <strong>FAIR PLAY</strong>
            <small>Play Fair, Win Big</small>
          </div>
        </div>

        <div style={styles.footerItem}>
          <span>🎁</span>
          <div>
            <strong>DAILY BONUS</strong>
            <small>Win More Every Day</small>
          </div>
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

  return <GameLobby />;
}

const styles = {
  page: {
    minHeight: "100vh",
    position: "relative",
    overflow: "hidden",
    color: "#fff",
    fontFamily: "Arial, sans-serif",
    padding: "28px 48px",
    backgroundImage:
      "linear-gradient(rgba(0,0,0,.55), rgba(0,0,0,.78)), url('/casino-assets/casino-bg.png')",
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
  },

  overlay: {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background:
      "radial-gradient(circle at 18% 18%, rgba(255,180,0,.18), transparent 28%), radial-gradient(circle at 88% 20%, rgba(179,0,255,.24), transparent 32%), linear-gradient(180deg, rgba(0,0,0,.15), rgba(0,0,0,.50))",
  },

  header: {
    position: "relative",
    zIndex: 2,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },

  brand: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    color: "#ffd65c",
    fontSize: 42,
    fontWeight: 1000,
    textShadow: "0 0 18px rgba(255,214,92,.55)",
  },

  crown: {
    fontSize: 52,
    color: "#ffd65c",
  },

  brandSub: {
    margin: "0 0 0 74px",
    color: "#f7d36a",
    letterSpacing: 5,
    fontWeight: 700,
  },

  topRight: {
    display: "flex",
    gap: 22,
    alignItems: "center",
  },

  balance: {
    height: 78,
    minWidth: 300,
    borderRadius: 18,
    background: "rgba(0,0,0,.55)",
    border: "1px solid rgba(255,255,255,.22)",
    display: "flex",
    alignItems: "center",
    gap: 16,
    padding: "0 18px",
    boxShadow: "0 12px 34px rgba(0,0,0,.55)",
    backdropFilter: "blur(8px)",
  },

  coin: {
    width: 42,
    height: 42,
    borderRadius: "50%",
    background: "linear-gradient(135deg, #ffcc31, #b66a00)",
    display: "grid",
    placeItems: "center",
    color: "#2b1200",
    fontWeight: 1000,
    fontSize: 26,
  },

  userBox: {
    height: 78,
    minWidth: 250,
    borderRadius: 18,
    background: "rgba(0,0,0,.55)",
    border: "1px solid rgba(255,255,255,.22)",
    display: "flex",
    alignItems: "center",
    gap: 14,
    padding: "0 18px",
    boxShadow: "0 12px 34px rgba(0,0,0,.55)",
    backdropFilter: "blur(8px)",
  },

  avatar: {
    width: 44,
    height: 44,
    borderRadius: "50%",
    background: "#e8e8e8",
    display: "grid",
    placeItems: "center",
  },

  hero: {
    position: "relative",
    zIndex: 2,
    textAlign: "center",
    marginTop: 4,
  },

  goldLine: {
    width: 440,
    height: 1,
    background: "linear-gradient(90deg, transparent, #d9a72c, transparent)",
    margin: "0 auto",
  },

  heroCrown: {
    color: "#ffc400",
    fontSize: 76,
    lineHeight: 1,
    textShadow: "0 0 22px rgba(255,196,0,.8)",
  },

  cards: {
    position: "relative",
    zIndex: 2,
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 28,
    marginTop: 30,
  },

  card: {
    position: "relative",
    minHeight: 510,
    border: "2px solid",
    borderRadius: 24,
    overflow: "hidden",
    padding: 22,
    textDecoration: "none",
    color: "#fff",
    background:
      "linear-gradient(180deg, rgba(255,255,255,.09), rgba(0,0,0,.55))",
    backdropFilter: "blur(8px)",
  },

  ribbon: {
    position: "absolute",
    top: 24,
    left: -42,
    transform: "rotate(-45deg)",
    width: 165,
    textAlign: "center",
    padding: "8px 0",
    fontWeight: 1000,
    fontSize: 20,
    zIndex: 3,
  },

  visual: {
    height: 315,
    width: "100%",
    borderRadius: 18,
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    boxShadow: "inset 0 -60px 80px rgba(0,0,0,.55)",
    marginBottom: 18,
  },

  playBtn: {
    position: "absolute",
    left: 38,
    right: 38,
    bottom: 34,
    height: 66,
    borderRadius: 18,
    border: "2px solid",
    background: "rgba(0,0,0,.42)",
    color: "#fff",
    fontSize: 26,
    fontWeight: 1000,
    cursor: "pointer",
  },

  footer: {
    position: "relative",
    zIndex: 2,
    maxWidth: 1400,
    margin: "40px auto 0",
    minHeight: 110,
    borderRadius: 28,
    background: "rgba(0,0,0,.58)",
    border: "1px solid rgba(255,255,255,.18)",
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    alignItems: "center",
    padding: "0 35px",
    backdropFilter: "blur(8px)",
  },

  footerItem: {
    display: "flex",
    alignItems: "center",
    gap: 16,
    color: "#fff",
  },
};
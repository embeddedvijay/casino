import React from "react";
import Aviator from "./games/aviator/Aviator.jsx";
import DragonTiger from "./games/dragon-tiger/DragonTiger.jsx";
import LuckyRace from "./games/car-roulet/LuckyRace.jsx";
import MatkaDashboard from "./games/matka/MatkaDashboard.jsx";

function GameLobby() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#101112",
        color: "white",
        padding: 30,
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Casino Games</h1>
      <p>Select game:</p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 16,
          maxWidth: 900,
          marginTop: 20,
        }}
      >
        <a
          href="/aviator"
          style={{
            textDecoration: "none",
            color: "white",
            background: "#181a1b",
            border: "1px solid #30383d",
            borderRadius: 16,
            padding: 20,
          }}
        >
          <h2 style={{ margin: 0, color: "#ff004f" }}>Aviator</h2>
          <p style={{ color: "#aab5ba" }}>Crash multiplier game</p>
        </a>

        <a
          href="/dragon-tiger"
          style={{
            textDecoration: "none",
            color: "white",
            background: "#181a1b",
            border: "1px solid #7f561c",
            borderRadius: 16,
            padding: 20,
          }}
        >
          <h2 style={{ margin: 0 }}>
            <span style={{ color: "#f23833" }}>Dragon</span>{" "}
            <span style={{ color: "#36a9ff" }}>Tiger</span>
          </h2>
          <p style={{ color: "#aab5ba" }}>Card comparison game</p>
        </a>

        <a
          href="/lucky-race"
          style={{
            textDecoration: "none",
            color: "white",
            background: "#181a1b",
            border: "1px solid #5b43ff",
            borderRadius: 16,
            padding: 20,
          }}
        >
          <h2 style={{ margin: 0, color: "#ffe600" }}>Lucky Race</h2>
          <p style={{ color: "#aab5ba" }}>Car roulette game</p>
        </a>

        <a
          href="/matka"
          style={{
            textDecoration: "none",
            color: "white",
            background: "#181a1b",
            border: "1px solid #8b5cf6",
            borderRadius: 16,
            padding: 20,
          }}
        >
          <h2 style={{ margin: 0, color: "#a855f7" }}>Matka</h2>
          <p style={{ color: "#aab5ba" }}>Matka booking dashboard</p>
        </a>
      </div>
    </div>
  );
}

export default function App() {
  const path = window.location.pathname;

  if (path === "/") {
    return <GameLobby />;
  }

  if (path === "/aviator") {
    return <Aviator />;
  }

  if (path === "/dragon-tiger") {
    return <DragonTiger />;
  }

  if (path === "/lucky-race") {
    return <LuckyRace />;
  }

  if (path === "/matka") {
    return <MatkaDashboard />;
  }

  return <GameLobby />;
}
import React from "react";
import Aviator from "./games/aviator/Aviator.jsx";
import DragonTiger from "./games/dragon-tiger/DragonTiger.jsx";

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
          maxWidth: 700,
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

  return <GameLobby />;
}
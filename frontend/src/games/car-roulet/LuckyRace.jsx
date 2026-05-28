import React, { useState } from "react";
import "./luckyRace.css";

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
  const [selectedCoin, setSelectedCoin] = useState(10);
  const [lastResults, setLastResults] = useState([
    "bmw",
    "ferrari",
    "jaguar",
    "land_rover",
    "maserati",
  ]);

  const [bets, setBets] = useState(
    Object.fromEntries(betCars.map((car) => [car, "0"]))
  );

  const handleBetChange = (car, value) => {
    const onlyNumber = value.replace(/\D/g, "");
    setBets((prev) => ({
      ...prev,
      [car]: onlyNumber || "0",
    }));
  };

  const placeCoinBet = (car) => {
    setBets((prev) => ({
      ...prev,
      [car]: String(Number(prev[car] || 0) + selectedCoin),
    }));
  };

  return (
    <div className="cr-page">
      <div className="cr-casino-bg">
        <span></span>
        <span></span>
        <span></span>
      </div>

      <div className="cr-result-panel">
        <span className="cr-result-title">LAST RESULT</span>

        <div className="cr-result-logos">
          {lastResults.map((car, index) => (
            <div className="cr-result-logo" key={`${car}-${index}`}>
              <img src={`${LOGO}${fileName(car)}`} alt={car} />
            </div>
          ))}
        </div>
      </div>

      <div className="cr-table">
        <div className="cr-outer">
          {logos.map(([logo, x, y], i) => (
            <div
              key={`${logo}-${i}`}
              className="cr-logo"
              style={{ left: `${x}%`, top: `${y}%` }}
            >
              <img src={`${LOGO}${fileName(logo)}`} alt={logo} />
            </div>
          ))}

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
                    value={bets[car]}
                    onClick={(e) => e.stopPropagation()}
                    onChange={(e) => handleBetChange(car, e.target.value)}
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
      </div>
    </div>
  );
}
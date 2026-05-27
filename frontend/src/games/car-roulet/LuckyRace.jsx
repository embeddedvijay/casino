import React from "react";
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

export default function LuckyRace() {
  return (
    <div className="cr-page">
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
        </div>
      </div>
    </div>
  );
}
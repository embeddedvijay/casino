import React from "react";
import "./luckyRace.css";

const LOGO = "/new-logos/";

const fileName = (name) =>
  name === "land_rover" ? "land_rover.png" : `${name}.png`;

const logos = [
  ["maserati", 26, 7],
  ["ferrari", 32, 7],
  ["lamborghini", 38, 7],
  ["porsche", 44, 7],
  ["bmw", 50, 7],
  ["mercedes", 56, 7],
  ["jaguar", 62, 7],
  ["land_rover", 68, 7],

  ["ferrari", 68, 7],
  ["lamborghini", 74, 7],
  ["porsche", 38, 7],
  ["maserati", 44, 7],
  ["ferrari", 50, 7],
  ["lamborghini", 56, 7],
  ["porsche", 62, 7],

  ["bmw", 82, 7],
  ["mercedes", 88, 12],
  ["jaguar", 93, 22],
  ["land_rover", 96, 37],
  ["maserati", 97, 52],

  ["ferrari", 96, 67],
  ["lamborghini", 92, 79],
  ["porsche", 87, 88],
  ["bmw", 81, 92],
  ["mercedes", 75, 92],
  ["jaguar", 69, 92],
  ["land_rover", 63, 92],

  ["ferrari", 57, 92],
  ["lamborghini", 51, 92],
  ["porsche", 45, 92],
  ["bmw", 39, 92],
  ["mercedes", 33, 92],
  ["jaguar", 27, 92],
  ["land_rover", 21, 92],

  ["ferrari", 15, 91],
  ["lamborghini", 10, 84],
  ["porsche", 6, 74],
  ["bmw", 3, 61],
  ["mercedes", 0, 55],
  ["jaguar", 27, 92],
  ["land_rover", 21, 92],
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
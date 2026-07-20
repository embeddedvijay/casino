import React, { useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import { api } from "../api";

const DEFAULT_MARKETS = [
  {
    key: "SRIDEVI_DAY",
    name: "SRIDEVI DAY",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "SRIDEVI_NIGHT",
    name: "SRIDEVI NIGHT",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "TIME_BAZAR_DAY",
    name: "TIME BAZAR DAY",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "MAIN_BAZAR_NIGHT",
    name: "MAIN BAZAR NIGHT",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "MADHUR_DAY",
    name: "MADHUR DAY",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "MADHUR_NIGHT",
    name: "MADHUR NIGHT",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "MILAN_DAY",
    name: "MILAN DAY",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "MILAN_NIGHT",
    name: "MILAN NIGHT",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "RAJDHANI_DAY",
    name: "RAJDHANI DAY",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "RAJDHANI_NIGHT",
    name: "RAJDHANI NIGHT",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "SUPREME_DAY",
    name: "SUPREME DAY",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "SUPREME_NIGHT",
    name: "SUPREME NIGHT",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "KALYAN_DAY",
    name: "KALYAN DAY",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
  {
    key: "KALYAN_NIGHT",
    name: "KALYAN NIGHT",
    enabled: true,
    open_time: "09:00",
    close_time: "23:00",
  },
];

export default function GameSettings() {
  const [settingType, setSettingType] = useState("");
  const [markets, setMarkets] = useState(DEFAULT_MARKETS);
  const [winRatio, setWinRatio] = useState(50);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (settingType === "matka") {
      loadMatkaSettings();
    }

    if (settingType === "casino") {
      loadCasinoWinRatio();
    }
  }, [settingType]);

  const loadMatkaSettings = async () => {
    setLoading(true);
    setMessage("");

    try {
      const response = await api("/api/admin/games/matka/markets");

      const savedMarkets = Array.isArray(response)
        ? response
        : response.markets || [];

      if (savedMarkets.length > 0) {
        const updatedMarkets = DEFAULT_MARKETS.map((defaultMarket) => {
          const savedMarket = savedMarkets.find(
            (market) => market.key === defaultMarket.key,
          );

          if (!savedMarket) {
            return defaultMarket;
          }

          return {
            ...defaultMarket,
            ...savedMarket,
            enabled:
              savedMarket.enabled !== undefined
                ? savedMarket.enabled
                : savedMarket.status === "Active",
          };
        });

        setMarkets(updatedMarkets);
      }
    } catch (error) {
      setMarkets(DEFAULT_MARKETS);
    } finally {
      setLoading(false);
    }
  };

  const loadCasinoWinRatio = async () => {
    setLoading(true);
    setMessage("");

    try {
      const response = await api("/api/admin/casino-settings");

      setWinRatio(
        Number(response.casino_win_ratio ?? 50),
      );
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  const updateMarket = (marketKey, field, value) => {
    setMarkets((currentMarkets) =>
      currentMarkets.map((market) => {
        if (market.key !== marketKey) {
          return market;
        }

        return {
          ...market,
          [field]: value,
        };
      }),
    );
  };

  const saveMatkaSettings = async () => {
    await api("/api/admin/games/matka/markets", {
      method: "PUT",
      body: JSON.stringify({
        markets,
      }),
    });
  };

  const saveCasinoWinRatio = async () => {
    await api("/api/admin/casino-settings/win-ratio", {
      method: "PATCH",
      body: JSON.stringify({
        casino_win_ratio: Number(winRatio),
      }),
    });
  };

  const saveSettings = async () => {
    setSaving(true);
    setMessage("");

    try {
      if (settingType === "matka") {
        await saveMatkaSettings();
      }

      if (settingType === "casino") {
        await saveCasinoWinRatio();
      }

      setMessage("Saved successfully");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  };

  const goBack = () => {
    setSettingType("");
    setMessage("");
  };

  return (
    <AdminLayout title="Game Settings">
      {!settingType && (
        <SettingTypePage
          onMatka={() => setSettingType("matka")}
          onCasino={() => setSettingType("casino")}
        />
      )}

      {settingType === "matka" && (
        <MatkaSettingsPage
          markets={markets}
          loading={loading}
          saving={saving}
          message={message}
          updateMarket={updateMarket}
          saveSettings={saveSettings}
          goBack={goBack}
        />
      )}

      {settingType === "casino" && (
        <CasinoWinRatioPage
          winRatio={winRatio}
          setWinRatio={setWinRatio}
          loading={loading}
          saving={saving}
          message={message}
          saveSettings={saveSettings}
          goBack={goBack}
        />
      )}
    </AdminLayout>
  );
}

function SettingTypePage({ onMatka, onCasino }) {
  return (
    <>
      <div className="ca-title">
        <div>
          <h1>Game Settings</h1>
          <p>Select setting type</p>
        </div>
      </div>

      <div className="ca-grid2">
        <button
          type="button"
          className="ca-card"
          onClick={onMatka}
          style={{
            cursor: "pointer",
            textAlign: "left",
          }}
        >
          <h2>Matka Settings</h2>

          <p>
            Market enable/disable और OP/CL time manage करें।
          </p>

          <span className="ca-link">
            Open Matka Settings →
          </span>
        </button>

        <button
          type="button"
          className="ca-card"
          onClick={onCasino}
          style={{
            cursor: "pointer",
            textAlign: "left",
          }}
        >
          <h2>Casino Win Ratio</h2>

          <p>
            Casino games का win ratio set करें।
          </p>

          <span className="ca-link">
            Open Win Ratio →
          </span>
        </button>
      </div>
    </>
  );
}

function MatkaSettingsPage({
  markets,
  loading,
  saving,
  message,
  updateMarket,
  saveSettings,
  goBack,
}) {
  return (
    <>
      <div className="ca-title">
        <div>
          <h1>Matka Settings</h1>
          <p>Market status और timing manage करें</p>
        </div>

        <button
          type="button"
          className="ca-link"
          onClick={goBack}
        >
          ← Back
        </button>
      </div>

      <section className="ca-card">
        {loading ? (
          <p>Loading markets...</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="ca-table">
              <thead>
                <tr>
                  <th>Market Name</th>
                  <th>Enable / Disable</th>
                  <th>OP Time</th>
                  <th>CL Time</th>
                </tr>
              </thead>

              <tbody>
                {markets.map((market) => (
                  <tr key={market.key}>
                    <td>
                      <b>{market.name}</b>
                    </td>

                    <td>
                      <label>
                        <input
                          type="checkbox"
                          checked={market.enabled}
                          onChange={(event) =>
                            updateMarket(
                              market.key,
                              "enabled",
                              event.target.checked,
                            )
                          }
                        />

                        {market.enabled
                          ? " Enabled"
                          : " Disabled"}
                      </label>
                    </td>

                    <td>
                      <input
                        type="time"
                        value={market.open_time}
                        onChange={(event) =>
                          updateMarket(
                            market.key,
                            "open_time",
                            event.target.value,
                          )
                        }
                      />
                    </td>

                    <td>
                      <input
                        type="time"
                        value={market.close_time}
                        onChange={(event) =>
                          updateMarket(
                            market.key,
                            "close_time",
                            event.target.value,
                          )
                        }
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <div className="ca-actions">
        {message && <span>{message}</span>}

        <button
          type="button"
          onClick={saveSettings}
          disabled={loading || saving}
        >
          {saving ? "Saving..." : "Save Matka Settings"}
        </button>
      </div>
    </>
  );
}

function CasinoWinRatioPage({
  winRatio,
  setWinRatio,
  loading,
  saving,
  message,
  saveSettings,
  goBack,
}) {
  return (
    <>
      <div className="ca-title">
        <div>
          <h1>Casino Win Ratio</h1>
          <p>Casino games का win ratio set करें</p>
        </div>

        <button
          type="button"
          className="ca-link"
          onClick={goBack}
        >
          ← Back
        </button>
      </div>

      <section className="ca-card">
        {loading ? (
          <p>Loading settings...</p>
        ) : (
          <div className="ca-form-grid">
            <label>
              Casino Win Ratio (%)

              <input
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={winRatio}
                onChange={(event) =>
                  setWinRatio(event.target.value)
                }
              />
            </label>
          </div>
        )}
      </section>

      <div className="ca-actions">
        {message && <span>{message}</span>}

        <button
          type="button"
          onClick={saveSettings}
          disabled={loading || saving}
        >
          {saving ? "Saving..." : "Save Win Ratio"}
        </button>
      </div>
    </>
  );
}
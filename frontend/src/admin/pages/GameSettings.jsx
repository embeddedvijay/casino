import React, { useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import { api } from "../api";
export default function GameSettings({ gameKey }) {
  const [form, setForm] = useState({
    key: gameKey,
    name: "",
    enabled: true,
    min_bet: 10,
    max_bet: 10000,
    house_edge: 1,
    max_multiplier: 100,
    waiting_seconds: 10,
    result_seconds: 5,
    description: "",
  });
  const [msg, setMsg] = useState("");
  useEffect(() => {
    api(`/api/admin/games/${gameKey}`)
      .then(setForm)
      .catch((e) => setMsg(e.message));
  }, [gameKey]);
  const change = (e) =>
    setForm({
      ...form,
      [e.target.name]:
        e.target.type === "checkbox" ? e.target.checked : e.target.value,
    });
  const save = async () => {
    try {
      await api(`/api/admin/games/${gameKey}`, {
        method: "PUT",
        body: JSON.stringify({
          ...form,
          min_bet: Number(form.min_bet),
          max_bet: Number(form.max_bet),
          house_edge: Number(form.house_edge),
          max_multiplier: Number(form.max_multiplier),
          waiting_seconds: Number(form.waiting_seconds),
          result_seconds: Number(form.result_seconds),
        }),
      });
      setMsg("Saved successfully");
    } catch (e) {
      setMsg(e.message);
    }
  };
  return (
    <AdminLayout title={`${form.name || gameKey} Settings`}>
      <div className="ca-title">
        <div>
          <h1>{form.name || gameKey}</h1>
          <p>Individual game configuration</p>
        </div>
        <a className="ca-link" href="/casino-admin/games">
          ← Back
        </a>
      </div>
      <section className="ca-card">
        <div className="ca-setting-row">
          <div>
            <b>Game Status</b>
            <p>Enable or disable this game.</p>
          </div>
          <input
            type="checkbox"
            name="enabled"
            checked={!!form.enabled}
            onChange={change}
          />
        </div>
        <div className="ca-form-grid">
          <label>
            Game Name
            <input name="name" value={form.name || ""} onChange={change} />
          </label>
          <label>
            Game Key
            <input value={form.key || gameKey} disabled />
          </label>
          <label>
            Minimum Bet
            <input
              type="number"
              name="min_bet"
              value={form.min_bet}
              onChange={change}
            />
          </label>
          <label>
            Maximum Bet
            <input
              type="number"
              name="max_bet"
              value={form.max_bet}
              onChange={change}
            />
          </label>
          <label>
            House Edge (%)
            <input
              type="number"
              step="0.01"
              name="house_edge"
              value={form.house_edge}
              onChange={change}
            />
          </label>
          <label>
            Max Multiplier
            <input
              type="number"
              name="max_multiplier"
              value={form.max_multiplier}
              onChange={change}
            />
          </label>
          <label>
            Waiting Seconds
            <input
              type="number"
              name="waiting_seconds"
              value={form.waiting_seconds}
              onChange={change}
            />
          </label>
          <label>
            Result Seconds
            <input
              type="number"
              name="result_seconds"
              value={form.result_seconds}
              onChange={change}
            />
          </label>
          <label className="ca-full">
            Description
            <textarea
              name="description"
              value={form.description || ""}
              onChange={change}
            />
          </label>
        </div>
      </section>
      <div className="ca-actions">
        {msg && <span>{msg}</span>}
        <button onClick={save}>Save Changes</button>
      </div>
    </AdminLayout>
  );
}
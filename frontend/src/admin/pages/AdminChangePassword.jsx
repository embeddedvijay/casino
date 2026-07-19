import React, { useState } from "react";
const HOST = window.location.hostname;
const API = `http://${HOST}:8085`;

export default function AdminChangePassword() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("Please complete all password fields.");
      return;
    }
    if (newPassword.length < 8) {
      setError("New password must contain at least 8 characters.");
      return;
    }
    if (
      !/[A-Z]/.test(newPassword) ||
      !/[a-z]/.test(newPassword) ||
      !/[0-9]/.test(newPassword)
    ) {
      setError("Use uppercase, lowercase and at least one number.");
      return;
    }
    if (newPassword === currentPassword) {
      setError("New password must be different from the current password.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("New password and confirm password do not match.");
      return;
    }
    const token = localStorage.getItem("casino_admin_token");
    if (!token) {
      window.location.replace("/casino-admin");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${API}/admin/change-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok)
        throw new Error(
          data.detail || data.message || "Password could not be changed.",
        );
      if (data.access_token || data.token)
        localStorage.setItem(
          "casino_admin_token",
          data.access_token || data.token,
        );
      sessionStorage.removeItem("casino_password_change_required");
      window.location.replace("/casino-admin/dashboard");
    } catch (err) {
      setError(err.message || "Password could not be changed.");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="change-page">
      <style>{`*{box-sizing:border-box}.change-page{min-height:100vh;display:grid;place-items:center;padding:24px;background:radial-gradient(circle at 20% 10%,rgba(124,58,237,.24),transparent 32%),radial-gradient(circle at 90% 90%,rgba(37,99,235,.18),transparent 35%),#070b14;color:#f8fafc;font-family:Inter,system-ui,sans-serif}.change-card{width:min(100%,470px);padding:42px;background:rgba(12,18,32,.88);border:1px solid rgba(148,163,184,.17);border-radius:25px;box-shadow:0 28px 80px rgba(0,0,0,.46);backdrop-filter:blur(18px)}.icon{width:58px;height:58px;display:grid;place-items:center;margin-bottom:25px;border-radius:17px;background:linear-gradient(135deg,#8b5cf6,#2563eb);font-size:27px;box-shadow:0 12px 30px rgba(79,70,229,.3)}.tag{margin:0 0 8px;color:#a78bfa;font-size:11px;font-weight:800;letter-spacing:2px;text-transform:uppercase}.change-card h1{margin:0;font-size:31px;letter-spacing:-1px}.intro{margin:10px 0 27px;color:#94a3b8;font-size:14px;line-height:1.6}.field{display:block;margin-bottom:16px}.field span{display:block;margin-bottom:8px;color:#cbd5e1;font-size:13px;font-weight:700}.password{position:relative}.password input{width:100%;height:51px;padding:0 46px 0 15px;border:1px solid #26324a;border-radius:12px;outline:none;background:#0a1220;color:#f8fafc;font-size:14px}.password input:focus{border-color:#8b5cf6;box-shadow:0 0 0 4px rgba(139,92,246,.12)}.password button{position:absolute;right:7px;top:50%;transform:translateY(-50%);width:36px;height:36px;border:0;border-radius:9px;background:transparent;color:#94a3b8;cursor:pointer;font-size:18px}.requirements{margin:2px 0 20px;padding:12px 14px;border-radius:11px;background:rgba(30,41,59,.52);color:#94a3b8;font-size:12px;line-height:1.6}.error{margin:0 0 16px;padding:11px 13px;border:1px solid rgba(248,113,113,.25);border-radius:11px;background:rgba(127,29,29,.16);color:#fca5a5;font-size:13px}.submit{width:100%;height:52px;border:0;border-radius:13px;background:linear-gradient(135deg,#8b5cf6,#2563eb);color:#fff;font-weight:800;cursor:pointer;box-shadow:0 12px 28px rgba(79,70,229,.25)}.submit:disabled{opacity:.65;cursor:not-allowed}@media(max-width:520px){.change-page{padding:14px}.change-card{padding:31px 24px}.change-card h1{font-size:27px}}`}</style>
      <main className="change-card">
        <div className="icon">🔐</div>
        <p className="tag">First login security</p>
        <h1>Create a new password</h1>
        <p className="intro">
          You are using a temporary password. Change it before accessing the
          admin dashboard.
        </p>
        <form onSubmit={submit}>
          <PasswordField
            label="Current password"
            value={currentPassword}
            setValue={setCurrentPassword}
            show={show}
          />
          <PasswordField
            label="New password"
            value={newPassword}
            setValue={setNewPassword}
            show={show}
          />
          <PasswordField
            label="Confirm new password"
            value={confirmPassword}
            setValue={setConfirmPassword}
            show={show}
          />
          <div className="requirements">
            Minimum 8 characters with uppercase, lowercase and a number.
          </div>
          {error && <div className="error">{error}</div>}
          <button className="submit" type="submit" disabled={loading}>
            {loading ? "Updating password..." : "Change password & continue"}
          </button>
          <button
            type="button"
            onClick={() => setShow((v) => !v)}
            style={{
              width: "100%",
              marginTop: 12,
              border: 0,
              background: "transparent",
              color: "#94a3b8",
              cursor: "pointer",
            }}
          >
            {show ? "Hide passwords" : "Show passwords"}
          </button>
        </form>
      </main>
    </div>
  );
}
function PasswordField({ label, value, setValue, show }) {
  return (
    <label className="field">
      <span>{label}</span>
      <div className="password">
        <input
          type={show ? "text" : "password"}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          autoComplete={
            label === "Current password" ? "current-password" : "new-password"
          }
          placeholder={`Enter ${label.toLowerCase()}`}
        />
      </div>
    </label>
  );
}
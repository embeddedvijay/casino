import React, { useState } from "react";
const HOST = window.location.hostname;
const API = `http://${HOST}:8085`;

export default function AdminLogin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!username.trim() || !password) {
      setError("Please enter username and password.");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${API}/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok)
        throw new Error(
          data.detail || data.message || "Invalid username or password.",
        );
      const token = data.access_token || data.token;
      if (!token) throw new Error("Login token was not received.");
      localStorage.setItem("casino_admin_token", token);
      localStorage.setItem(
        "casino_admin",
        JSON.stringify(data.admin || { username: username.trim() }),
      );
      if (
        data.must_change_password === true ||
        data.admin?.must_change_password === true
      ) {
        sessionStorage.setItem("casino_password_change_required", "true");
        window.location.href = "/casino-admin/change-password";
        return;
      }
      sessionStorage.removeItem("casino_password_change_required");
      window.location.href = "/casino-admin/dashboard";
    } catch (err) {
      setError(err.message || "Unable to login. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="admin-login-page">
      <style>{`
*{box-sizing:border-box}.admin-login-page{min-height:100vh;display:grid;place-items:center;padding:24px;color:#f8fafc;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 15% 15%,rgba(124,58,237,.24),transparent 32%),radial-gradient(circle at 85% 80%,rgba(14,165,233,.17),transparent 32%),#070b14;position:relative;overflow:hidden}.admin-login-page:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:42px 42px;mask-image:linear-gradient(to bottom,black,transparent)}.login-shell{width:min(100%,980px);min-height:610px;display:grid;grid-template-columns:1.05fr .95fr;background:rgba(10,16,29,.78);border:1px solid rgba(148,163,184,.16);border-radius:28px;overflow:hidden;box-shadow:0 32px 90px rgba(0,0,0,.48);backdrop-filter:blur(18px);position:relative}.login-brand{padding:58px;display:flex;flex-direction:column;justify-content:space-between;background:linear-gradient(145deg,rgba(124,58,237,.23),rgba(15,23,42,.28));border-right:1px solid rgba(148,163,184,.12)}.brand-mark{width:58px;height:58px;display:grid;place-items:center;border-radius:18px;font-size:28px;background:linear-gradient(135deg,#8b5cf6,#2563eb);box-shadow:0 14px 35px rgba(79,70,229,.35)}.brand-copy h1{font-size:clamp(38px,5vw,58px);line-height:1.02;letter-spacing:-2.5px;margin:28px 0 18px}.brand-copy h1 span{background:linear-gradient(90deg,#c4b5fd,#7dd3fc);-webkit-background-clip:text;color:transparent}.brand-copy p{max-width:400px;margin:0;color:#94a3b8;font-size:16px;line-height:1.75}.security-note{display:flex;gap:10px;align-items:center;color:#94a3b8;font-size:13px}.security-note i{width:9px;height:9px;border-radius:50%;background:#22c55e;box-shadow:0 0 14px #22c55e}.login-panel{padding:58px 54px;display:flex;flex-direction:column;justify-content:center}.eyebrow{margin:0 0 10px;color:#a78bfa;text-transform:uppercase;letter-spacing:2px;font-size:12px;font-weight:800}.login-panel h2{font-size:32px;letter-spacing:-1px;margin:0}.login-subtitle{color:#94a3b8;margin:10px 0 30px;font-size:14px}.field{display:block;margin-bottom:18px}.field-label{display:block;color:#cbd5e1;font-size:13px;font-weight:700;margin:0 0 9px}.input-wrap{position:relative}.input-wrap svg{position:absolute;left:15px;top:50%;transform:translateY(-50%);width:19px;height:19px;color:#64748b}.input-wrap input{width:100%;height:52px;border:1px solid #253149;border-radius:13px;background:#0b1220;color:#f8fafc;padding:0 46px;font-size:15px;outline:none;transition:.2s}.input-wrap input::placeholder{color:#475569}.input-wrap input:focus{border-color:#8b5cf6;box-shadow:0 0 0 4px rgba(139,92,246,.12)}.password-toggle{position:absolute;right:8px;top:50%;transform:translateY(-50%);height:36px;width:36px;border:0;border-radius:9px;color:#94a3b8;background:transparent;cursor:pointer;font-size:18px}.password-toggle:hover{background:#162033;color:#fff}.login-error{padding:11px 13px;margin:-4px 0 17px;border:1px solid rgba(248,113,113,.25);border-radius:11px;background:rgba(127,29,29,.16);color:#fca5a5;font-size:13px}.login-button{width:100%;height:52px;border:0;border-radius:13px;background:linear-gradient(135deg,#8b5cf6,#2563eb);color:white;font-size:15px;font-weight:800;cursor:pointer;box-shadow:0 12px 28px rgba(79,70,229,.25);transition:.2s}.login-button:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 16px 34px rgba(79,70,229,.35)}.login-button:disabled{opacity:.65;cursor:not-allowed}.login-footer{text-align:center;color:#64748b;font-size:12px;margin:24px 0 0}@media(max-width:760px){.admin-login-page{padding:14px}.login-shell{grid-template-columns:1fr;min-height:auto}.login-brand{padding:30px;border-right:0;border-bottom:1px solid rgba(148,163,184,.12)}.brand-copy h1{font-size:36px;margin:18px 0 10px}.brand-copy p,.security-note{display:none}.login-panel{padding:36px 28px 38px}.login-panel h2{font-size:28px}}
`}</style>
      <main className="login-shell">
        <section className="login-brand">
          <div>
            <div className="brand-mark">♠</div>
            <div className="brand-copy">
              <h1>
                Casino
                <br />
                <span>Command Center</span>
              </h1>
              <p>
                Manage games, monitor activity and control your casino
                operations from one secure dashboard.
              </p>
            </div>
          </div>
          <div className="security-note">
            <i />
            Protected admin access
          </div>
        </section>
        <section className="login-panel">
          <p className="eyebrow">Administrator Portal</p>
          <h2>Welcome back</h2>
          <p className="login-subtitle">Enter your credentials to continue.</p>
          <form onSubmit={handleSubmit}>
            <label className="field">
              <span className="field-label">Username</span>
              <span className="input-wrap">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M20 21a8 8 0 0 0-16 0" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                <input
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter admin username"
                  autoComplete="username"
                  autoFocus
                />
              </span>
            </label>
            <label className="field">
              <span className="field-label">Password</span>
              <span className="input-wrap">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="3" y="11" width="18" height="10" rx="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
                <button
                  className="password-toggle"
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "◉" : "◎"}
                </button>
              </span>
            </label>
            {error && <div className="login-error">{error}</div>}
            <button className="login-button" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign in to dashboard"}
            </button>
          </form>
          <p className="login-footer">Authorized personnel only</p>
        </section>
      </main>
    </div>
  );
}
import React from "react";
import AdminLogin from "./pages/AdminLogin";
import AdminChangePassword from "./pages/AdminChangePassword";
import AdminDashboard from "./pages/AdminDashboard";
import CasinoSettings from "./pages/CasinoSettings";
import GameSettings from "./pages/GameSettings";
import Management from "./pages/Management";

export default function AdminRouter() {
  const path = window.location.pathname;
  const changeRequired =
    sessionStorage.getItem("casino_password_change_required") === "true";

  if (path === "/casino-admin" || path === "/casino-admin/") {
    return <AdminLogin />;
  }

  if (path === "/casino-admin/change-password") {
    return <AdminChangePassword />;
  }

  if (changeRequired) {
    window.location.replace("/casino-admin/change-password");
    return null;
  }

  if (path === "/casino-admin/settings") {
    return <CasinoSettings />;
  }

  if (
    path === "/casino-admin/games" ||
    path.startsWith("/casino-admin/games/")
  ) {
    window.history.replaceState(null, "", "/casino-admin/game-settings");
    return <GameSettings />;
  }

  if (path === "/casino-admin/game-settings") {
    return <GameSettings />;
  }

  if (path === "/casino-admin/management") {
    return <Management />;
  }

  return <AdminDashboard />;
}

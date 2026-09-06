import React, { useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";
import { api } from "../api";
export default function AdminDashboard() {
  const [stats, setStats] = useState({
    users: 0,
    deposits: 0,
    withdrawals: 0,
    active_games: 0,
  });
  useEffect(() => {
    api("/api/admin/management/summary")
      .then(setStats)
      .catch(() => {});
  }, []);
  return (
    <AdminLayout title="Dashboard">
      <div className="ca-grid4">
        <div className="ca-stat">
          <span>Users</span>
          <b>{stats.users}</b>
        </div>
        <div className="ca-stat">
          <span>Total Deposits</span>
          <b>₹ {Number(stats.deposits || 0).toFixed(2)}</b>
        </div>
        <div className="ca-stat">
          <span>Total Withdrawals</span>
          <b>₹ {Number(stats.withdrawals || 0).toFixed(2)}</b>
        </div>
        <div className="ca-stat">
          <span>Active Games</span>
          <b>{stats.active_games}</b>
        </div>
      </div>
    </AdminLayout>
  );
}
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getStats, getTickets } from "../api";

const PRIORITY_STYLE = {
  high: "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-green-100 text-green-700",
};

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl border p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-2xl font-semibold mt-1">{value}</p>
    </div>
  );
}

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [error, setError] = useState(false);

  async function load() {
    try {
      setError(false);
      const [s, t] = await Promise.all([getStats(), getTickets()]);
      setStats(s);
      setTickets(t);
    } catch {
      setError(true);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (error) return <p className="m-auto text-red-600">Could not load data. Is the backend running?</p>;
  if (!stats) return <p className="m-auto text-gray-400">Loading…</p>;

  return (
    <div className="max-w-5xl w-full mx-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Admin Dashboard</h1>
        <button onClick={load} className="text-sm text-indigo-600 hover:underline">↻ Refresh</button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatCard label="Conversations" value={stats.total_conversations} />
        <StatCard label="Messages" value={stats.total_messages} />
        <StatCard label="Escalated" value={stats.escalated_conversations} />
        <StatCard label="AI resolution rate" value={`${stats.resolution_rate}%`} />
        <StatCard label="Open tickets" value={stats.open_tickets} />
      </div>

      <div className="bg-white rounded-xl border p-4">
        <h2 className="text-sm font-medium mb-3">Conversations (last 7 days)</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.conversations_per_day}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" fontSize={12} />
              <YAxis allowDecimals={false} fontSize={12} />
              <Tooltip />
              <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-xl border overflow-x-auto">
        <h2 className="text-sm font-medium p-4 pb-2">Recent tickets</h2>
        <table className="w-full text-sm">
          <thead className="text-left text-gray-500 border-b">
            <tr>
              <th className="px-4 py-2">#</th>
              <th className="px-4 py-2">Customer</th>
              <th className="px-4 py-2">Issue</th>
              <th className="px-4 py-2">Priority</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Created</th>
            </tr>
          </thead>
          <tbody>
            {tickets.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-gray-400">No tickets yet</td>
              </tr>
            )}
            {tickets.map((t) => (
              <tr key={t.id} className="border-b last:border-0">
                <td className="px-4 py-2">{t.id}</td>
                <td className="px-4 py-2">{t.customer}</td>
                <td className="px-4 py-2 max-w-xs truncate" title={t.issue}>{t.issue}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs ${PRIORITY_STYLE[t.priority] || ""}`}>{t.priority}</span>
                </td>
                <td className="px-4 py-2">{t.status}</td>
                <td className="px-4 py-2 whitespace-nowrap">{t.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
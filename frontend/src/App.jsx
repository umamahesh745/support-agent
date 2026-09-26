import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import Chat from "./pages/Chat";
import Admin from "./pages/Admin";

const linkClass = ({ isActive }) =>
  `px-3 py-1.5 rounded-lg text-sm font-medium ${
    isActive ? "bg-indigo-600 text-white" : "text-gray-600 hover:bg-gray-100"
  }`;

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <header className="bg-white border-b">
          <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
            <span className="font-bold text-lg text-indigo-600">🛍️ ShopEasy Support</span>
            <nav className="flex gap-2">
              <NavLink to="/" end className={linkClass}>Chat</NavLink>
              <NavLink to="/admin" className={linkClass}>Admin</NavLink>
            </nav>
          </div>
        </header>

        <main className="flex-1 flex">
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
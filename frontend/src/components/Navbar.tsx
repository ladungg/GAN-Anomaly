import { LogOut } from "lucide-react";

interface NavbarProps {
  username?: string;
  isAdmin?: boolean;
}

export function Navbar({ username, isAdmin }: NavbarProps) {
  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <nav className="bg-blue-600 text-white p-4 shadow-lg">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-bold">🔐 GAN Anomaly Detection</h1>
          <div className="flex gap-4">
            <a
              href="/dashboard"
              className="hover:bg-blue-700 px-3 py-2 rounded flex items-center gap-2"
            >
              📊 Dashboard
            </a>
            {isAdmin && (
              <a
                href="/admin"
                className="hover:bg-blue-700 px-3 py-2 rounded flex items-center gap-2"
              >
                ⚙️ Admin
              </a>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {username && <span className="text-sm">👤 {username}</span>}
          <button
            onClick={handleLogout}
            className="hover:bg-red-700 px-3 py-2 rounded flex items-center gap-2 transition"
          >
            <LogOut size={16} /> Đăng xuất
          </button>
        </div>
      </div>
    </nav>
  );
}

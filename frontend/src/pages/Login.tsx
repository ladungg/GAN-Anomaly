import { useState } from "react";
import PageHeader from "../components/PageHeader";
import { Card, CardContent } from "../components/Card";
import { Button } from "../components/Button";

const API_BASE = "http://127.0.0.1:8000";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError("");

    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) throw new Error();

      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", data.role || "user");
      localStorage.setItem("username", username);

      window.location.href = "/dashboard";
    } catch {
      setError("Tên đăng nhập hoặc mật khẩu không đúng");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <PageHeader />

      {/* CENTER CONTENT */}
      <div className="flex-1 flex items-center justify-center">
        <Card className="w-full max-w-md shadow-md">
          <CardContent className="space-y-5">
            <h2 className="text-2xl font-semibold text-center">
              Đăng nhập
            </h2>

            <div>
              <label className="text-sm font-medium">Tên đăng nhập</label>
              <input
                className="w-full border rounded px-3 py-2 mt-1"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Mật khẩu</label>
              <input
                type="password"
                className="w-full border rounded px-3 py-2 mt-1"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && (
              <p className="text-red-600 text-sm text-center">{error}</p>
            )}

            <Button className="w-full" onClick={handleLogin}>
              Đăng nhập
            </Button>

            <p className="text-sm text-center">
              Chưa có tài khoản?{" "}
              <a href="/register" className="text-blue-600 underline">
                Đăng ký
              </a>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

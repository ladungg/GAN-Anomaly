import { useState } from "react";
import PageHeader from "../components/PageHeader";
import { Card, CardContent } from "../components/Card";
import { Button } from "../components/Button";

const API_BASE = "http://127.0.0.1:8000";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleRegister = async () => {
    setError("");
    setSuccess("");

    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      if (!res.ok) throw new Error();

      setSuccess("Đăng ký thành công! Vui lòng đăng nhập.");
    } catch {
      setError("Tên đăng nhập hoặc email đã tồn tại");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <PageHeader />

      <div className="flex-1 flex items-center justify-center">
        <Card className="w-full max-w-md shadow-md">
          <CardContent className="space-y-5">
            <h2 className="text-2xl font-semibold text-center">
              Đăng ký tài khoản
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
              <label className="text-sm font-medium">Email</label>
              <input
                className="w-full border rounded px-3 py-2 mt-1"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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

            {success && (
              <p className="text-green-600 text-sm text-center">{success}</p>
            )}

            <Button className="w-full" onClick={handleRegister}>
              Đăng ký
            </Button>

            <p className="text-sm text-center">
              Đã có tài khoản?{" "}
              <a href="/login" className="text-blue-600 underline">
                Đăng nhập
              </a>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

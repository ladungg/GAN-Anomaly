import { useEffect, useState } from "react";
import { Card, CardContent } from "../components/Card";
import { Button } from "../components/Button";
import { Navbar } from "../components/Navbar";
import { Trash2 } from "lucide-react";

const API_BASE = "http://127.0.0.1:8000";

type InferenceHistory = {
  id: number;
  fileName: string;
  timestamp: string;
  total: number;
  normal: number;
  attack: number;
  normal_percentage: number;
  attack_percentage: number;
  downloadFileName?: string;
};

export default function Dashboard() {
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("user");

  // === FILE UPLOAD & INFERENCE STATES ===
  const [inferenceFile, setInferenceFile] = useState<File | null>(null);
  const [inferenceStatus, setInferenceStatus] = useState("");
  const [inferenceResult, setInferenceResult] = useState<{
    total: number;
    normal: number;
    attack: number;
    normal_percentage: number;
    attack_percentage: number;
  } | null>(null);
  const [isInferencing, setIsInferencing] = useState(false);
  const [history, setHistory] = useState<InferenceHistory[]>([]);
  const [downloadFileName, setDownloadFileName] = useState("");
  const [showDownloadButton, setShowDownloadButton] = useState(false);

  /* ======================
     LOAD INITIAL DATA
     ====================== */
  useEffect(() => {
    const storedUsername = localStorage.getItem("username") || "User";
    const storedRole = localStorage.getItem("role") || "user";
    setUsername(storedUsername);
    setRole(storedRole);
    
    // Load inference history from localStorage
    const storedHistory = localStorage.getItem("inferenceHistory");
    if (storedHistory) {
      try {
        setHistory(JSON.parse(storedHistory));
      } catch (e) {
        console.error("Failed to load history:", e);
      }
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("inferenceHistory", JSON.stringify(history));
  }, [history]);

  /* ======================
     STREAM TRAIN / TEST
     ====================== */
  // Kept for potential future use
  // const runStream = (endpoint: "train" | "test") => {
  //   ...
  // };

  /* ======================
     FILE INFERENCE
     ====================== */
  const handleInferenceFile = async () => {
    if (!inferenceFile) {
      setInferenceStatus("❌ Vui lòng chọn file");
      return;
    }

    setInferenceStatus("⏳ Đang kiểm tra file....");
    setIsInferencing(true);

    try {
      const formData = new FormData();
      formData.append("file", inferenceFile);

      const res = await fetch(`${API_BASE}/api/inference/predict`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Inference failed");

      const data = await res.json();
      
      // Calculate percentages
      const total = data.normal_count + data.attack_count;
      const normal_percentage = total > 0 ? (data.normal_count / total) * 100 : 0;
      const attack_percentage = total > 0 ? (data.attack_count / total) * 100 : 0;

      const result = {
        total,
        normal: data.normal_count,
        attack: data.attack_count,
        normal_percentage,
        attack_percentage,
      };

      setInferenceResult(result);

      // Add to history with download filename
      const newEntry: InferenceHistory = {
        id: Date.now(),
        fileName: inferenceFile.name,
        timestamp: new Date().toLocaleString("vi-VN"),
        total,
        normal: data.normal_count,
        attack: data.attack_count,
        normal_percentage,
        attack_percentage,
        downloadFileName: data.download_filename,
      };
      setHistory((prev) => [newEntry, ...prev]);
      
      // Show download button
      setDownloadFileName(data.download_filename);
      setShowDownloadButton(true);

      setInferenceStatus("✅ Kiểm tra hoàn tất!");
      setInferenceFile(null);
    } catch (e) {
      setInferenceStatus(`❌ Lỗi: ${(e as Error).message}`);
      setInferenceResult(null);
    } finally {
      setIsInferencing(false);
    }
  };

  /* ======================
     ROC DATA
     ====================== */
  // (Kept for potential future use in charts)

  /* ======================
     DOWNLOAD RESULT FILE
     ====================== */
  const handleDownloadResult = async (fileName: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/inference/download/${fileName}`
      );

      if (!response.ok) {
        alert("❌ Không thể tải file");
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      alert(`❌ Lỗi tải file: ${(e as Error).message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar username={username} isAdmin={role === "admin"} />

      <div className="p-14">
        <div className="mb-8 text-center space-y-3">
          <h1 className="text-2xl font-bold">
            🔍 BẢNG ĐIỀU KHIỂN PHÁT HIỆN BẤT THƯỜNG
          </h1>
          <p className="text-sm text-gray-600">
            Mô hình: <span className="font-semibold">🤖 GAN Anomaly</span> • 
            Bộ dữ liệu: <span className="font-semibold">📊 NSL-KDD</span>
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* FILE UPLOAD */}
        <Card className="md:col-span-1">
          <CardContent className="space-y-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              📁 Tải file kiểm tra
            </h2>

            <div className="border-2 border-dashed rounded p-6 text-center">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setInferenceFile(e.target.files?.[0] || null)}
                className="hidden"
                id="inference-file"
              />
              <label
                htmlFor="inference-file"
                className="cursor-pointer block space-y-3"
              >
                <div className="text-4xl">📄</div>
                <p className="text-sm font-medium">
                  {inferenceFile ? inferenceFile.name : "Chọn file CSV"}
                </p>
                <p className="text-xs text-gray-500">
                  (Nhấp để chọn)
                </p>
              </label>
            </div>

            <Button
              className="w-full"
              onClick={handleInferenceFile}
              disabled={!inferenceFile || isInferencing}
            >
              {isInferencing ? "⏳ Đang kiểm tra..." : "🔍 Chạy kiểm tra"}
            </Button>

            {inferenceStatus && (
              <div className={`p-3 rounded text-sm text-center ${
                inferenceStatus.includes("✅")
                  ? "bg-green-100 border border-green-300 text-green-800"
                  : "bg-red-100 border border-red-300 text-red-800"
              }`}>
                {inferenceStatus}
              </div>
            )}
          </CardContent>
        </Card>

        {/* RESULTS */}
        <Card className="md:col-span-2">
          <CardContent>
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              📊 Kết quả kiểm tra
            </h2>

            {inferenceResult ? (
              <div className="space-y-4">
                {/* SUMMARY */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-blue-50 border border-blue-200 rounded p-4 text-center">
                    <p className="text-sm text-gray-600">Tổng số mẫu</p>
                    <p className="text-3xl font-bold text-blue-600">{inferenceResult.total}</p>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded p-4 text-center">
                    <p className="text-sm text-gray-600">Bình thường</p>
                    <p className="text-3xl font-bold text-green-600">{inferenceResult.normal}</p>
                    <p className="text-xs text-gray-500">{inferenceResult.normal_percentage.toFixed(2)}%</p>
                  </div>
                  <div className="bg-red-50 border border-red-200 rounded p-4 text-center">
                    <p className="text-sm text-gray-600">Tấn công</p>
                    <p className="text-3xl font-bold text-red-600">{inferenceResult.attack}</p>
                    <p className="text-xs text-gray-500">{inferenceResult.attack_percentage.toFixed(2)}%</p>
                  </div>
                </div>

                {/* VISUAL BAR */}
                <div className="bg-gray-100 rounded p-4">
                  <p className="text-sm font-semibold mb-2">Tỷ lệ phân loại</p>
                  <div className="flex h-8 rounded overflow-hidden border border-gray-300">
                    <div
                      className="bg-green-500 flex items-center justify-center text-white text-xs font-bold"
                      style={{ width: `${inferenceResult.normal_percentage}%` }}
                    >
                      {inferenceResult.normal_percentage > 5 && `${inferenceResult.normal_percentage.toFixed(1)}%`}
                    </div>
                    <div
                      className="bg-red-500 flex items-center justify-center text-white text-xs font-bold"
                      style={{ width: `${inferenceResult.attack_percentage}%` }}
                    >
                      {inferenceResult.attack_percentage > 5 && `${inferenceResult.attack_percentage.toFixed(1)}%`}
                    </div>
                  </div>
                  <div className="flex gap-4 mt-2 text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded"></div>
                      <span>Bình thường</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded"></div>
                      <span>Tấn công</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                <p>Tải file CSV để xem kết quả kiểm tra</p>
              </div>
            )}

            {showDownloadButton && downloadFileName && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleDownloadResult(downloadFileName)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 transition"
                >
                  ⬇️ Tải file kết quả (CSV có đánh dấu)
                </button>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  File sẽ có cột "prediction_status" đánh dấu NORMAL hoặc ATTACK
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* LOG PANEL */}
      <Card className="mt-6">
        <CardContent>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">📜 Lịch sử kiểm tra</h2>
            {history.length > 0 && (
              <button
                onClick={() => {
                  setHistory([]);
                  localStorage.removeItem("inferenceHistory");
                }}
                className="text-sm px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
              >
                🗑️ Xóa lịch sử
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <p>Chưa có lịch sử kiểm tra</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Tên file</th>
                    <th className="text-center p-2">Thời gian</th>
                    <th className="text-center p-2">Tổng mẫu</th>
                    <th className="text-center p-2">Bình thường</th>
                    <th className="text-center p-2">Tấn công</th>
                    <th className="text-center p-2">Hành động</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((entry) => (
                    <tr key={entry.id} className="border-b hover:bg-gray-50">
                      <td className="p-2">{entry.fileName}</td>
                      <td className="text-center p-2 text-gray-600">{entry.timestamp}</td>
                      <td className="text-center p-2 font-semibold">{entry.total}</td>
                      <td className="text-center p-2">
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                          {entry.normal} ({entry.normal_percentage.toFixed(1)}%)
                        </span>
                      </td>
                      <td className="text-center p-2">
                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded">
                          {entry.attack} ({entry.attack_percentage.toFixed(1)}%)
                        </span>
                      </td>
                      <td className="text-center p-2 flex justify-center gap-2">
                        {entry.downloadFileName ? (
                          <button
                            onClick={() => handleDownloadResult(entry.downloadFileName!)}
                            className="text-blue-500 hover:text-blue-700 font-semibold text-sm px-2 py-1 bg-blue-50 rounded hover:bg-blue-100 transition"
                            title="Tải file kết quả"
                          >
                            ⬇️ Tải
                          </button>
                        ) : null}
                        <button
                          onClick={() => setHistory((prev) => prev.filter((h) => h.id !== entry.id))}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
      </div>
    </div>
  );
}

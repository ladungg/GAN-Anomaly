import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent } from "../components/Card";
import { Button } from "../components/Button";
import { Navbar } from "../components/Navbar";
import {
  Upload,
  Settings,
  Play,
  FileText,
  TrendingUp,
  BarChart3,
  Grid,
} from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
} from "recharts";

const API_BASE = "http://127.0.0.1:8000";

/* ======================
   TYPES
   ====================== */
type TrainingConfig = {
  niter: number;
  lr: number;
  beta1: number;
  w_adv: number;
  w_con: number;
  w_enc: number;
};

type InferenceLogs = {
  log_id: number;
  csv_filename: string;
  total_samples: number;
  normal_count: number;
  anomaly_count: number;
  anomaly_percentage: number;
  created_at: string;
};

type Metrics = {
  roc_auc: number;
  avg_runtime_ms: number;
  max_roc: number;
  roc_history: number[];
};

type ConfusionMatrix = {
  matrix: number[][];
  tn: number;
  fp: number;
  fn: number;
  tp: number;
};

type UploadedFile = {
  upload_id: number;
  filename: string;
  num_rows: number;
  num_features: number;
  created_at: string;
};

export default function Admin() {
  // State variables
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [activeTab, setActiveTab] = useState<
    "upload" | "config" | "train" | "logs" | "files"
  >("upload");
  const [username, setUsername] = useState("");
  const [trainingFile, setTrainingFile] = useState<File | null>(null);
  const [trainingStatus, setTrainingStatus] = useState("");
  const [trainingLogs, setTrainingLogs] = useState<string[]>([]);
  const [isTraining, setIsTraining] = useState(false);
  const [inferenceLogs, setInferenceLogs] = useState<InferenceLogs[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);

  const [config, setConfig] = useState<TrainingConfig>({
    niter: 5,
    lr: 0.0002,
    beta1: 0.5,
    w_adv: 1,
    w_con: 50,
    w_enc: 1,
  });

  const [configSaveStatus, setConfigSaveStatus] = useState("");

  // === METRICS STATES ===
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [confusion, setConfusion] = useState<ConfusionMatrix | null>(null);
  const [scores, setScores] = useState<number[]>([]);

  // === UPLOADED FILES STATE ===
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [loadingFiles, setLoadingFiles] = useState(false);

  // Use ref to track if we've initialized
  const initRef = useRef(false);

  /* ======================
     LOAD INFERENCE LOGS
     ====================== */
  const loadInferenceLogs = useCallback(async () => {
    setLoadingLogs(true);
    try {
      const res = await fetch(`${API_BASE}/api/inference/logs`);
      if (!res.ok) throw new Error("Failed to fetch logs");
      const data = await res.json();
      if (data.logs) {
        setInferenceLogs(data.logs);
      }
    } catch (e) {
      console.error("Failed to load inference logs:", e);
    } finally {
      setLoadingLogs(false);
    }
  }, []);

  /* ======================
     LOAD UPLOADED FILES
     ====================== */
  const loadUploadedFiles = useCallback(async () => {
    setLoadingFiles(true);
    try {
      const res = await fetch(`${API_BASE}/api/inference/uploads`);
      if (!res.ok) throw new Error("Failed to fetch uploads");
      const data = await res.json();
      if (data.uploads && Array.isArray(data.uploads)) {
        setUploadedFiles(data.uploads);
      }
    } catch (e) {
      console.error("Failed to load uploaded files:", e);
    } finally {
      setLoadingFiles(false);
    }
  }, []);

  /* ======================
     LOAD TRAINING METRICS
     ====================== */
  const loadTrainingMetrics = useCallback(async () => {
    try {
      const [metricsRes, confusionRes, scoresRes] = await Promise.all([
        fetch(`${API_BASE}/api/metrics`),
        fetch(`${API_BASE}/api/confusion-matrix`),
        fetch(`${API_BASE}/api/anomaly-scores`),
      ]);

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }

      if (confusionRes.ok) {
        const confusionData = await confusionRes.json();
        setConfusion(confusionData);
      }

      if (scoresRes.ok) {
        const scoresData = await scoresRes.json();
        setScores(scoresData.scores ?? []);
      }
    } catch (e) {
      console.error("Failed to load training metrics:", e);
    }
  }, []);

  /* ======================
     LOAD CONFIG FROM FILE
     ====================== */
  const loadConfig = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/training/get-config`);
      if (!res.ok) throw new Error("Failed to fetch config");
      const data = await res.json();
      if (data.status === "success" && data.config) {
        setConfig(data.config);
      }
    } catch (e) {
      console.error("Failed to load config:", e);
    }
  }, []);

  /* ======================
     INITIALIZATION EFFECT
     ====================== */
  useEffect(() => {
    if (initRef.current) return; // Only run once
    initRef.current = true;

    // Check role - only allow admin
    const role = localStorage.getItem("role");
    if (role !== "admin") {
      window.location.href = "/dashboard";
      return;
    }

    // Load username from localStorage
    const storedUsername = localStorage.getItem("username") || "Admin";
    setUsername(storedUsername);
    
    // Load config from file
    loadConfig();
    
    // Set authorization
    setIsAuthorized(true);
  }, [loadConfig]);

  /* ======================
     LOAD LOGS WHEN TAB CHANGES
     ====================== */
  useEffect(() => {
    if (activeTab === "logs" && isAuthorized) {
      loadInferenceLogs();
    }
  }, [activeTab, isAuthorized, loadInferenceLogs]);

  useEffect(() => {
    if (activeTab === "files" && isAuthorized) {
      loadUploadedFiles();
    }
  }, [activeTab, isAuthorized, loadUploadedFiles]);

  useEffect(() => {
    if (activeTab === "train" && isAuthorized) {
      loadTrainingMetrics();
    }
  }, [activeTab, isAuthorized, loadTrainingMetrics]);

  /* ======================
     UPLOAD TRAINING DATA
     ====================== */
  const handleUploadTrainingData = async () => {
    if (!trainingFile) {
      setTrainingStatus("❌ Vui lòng chọn file");
      return;
    }

    setTrainingStatus("⏳ Đang tải lên...");

    try {
      const formData = new FormData();
      formData.append("file", trainingFile);

      const res = await fetch(`${API_BASE}/api/training/upload-data`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setTrainingStatus(
          `✅ Tải lên thành công! ${data.num_rows} rows, ${data.num_features} features`
        );
        setTrainingFile(null);
      } else {
        setTrainingStatus(`❌ ${data.message || "Tải lên thất bại"}`);
      }
    } catch (e) {
      setTrainingStatus(`❌ Lỗi: ${(e as Error).message}`);
    }
  };

  /* ======================
     RUN TRAINING
     ====================== */
  const handleRunTraining = async () => {
    setIsTraining(true);
    setTrainingLogs([]);

    try {
      const res = await fetch(`${API_BASE}/api/training/train`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });

      if (!res.ok) {
        setTrainingLogs([
          `❌ Lỗi: ${(await res.json()).message || "Không thể bắt đầu training"}`,
        ]);
        setIsTraining(false);
        return;
      }

      // Stream logs
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter((l) => l.trim());

        setTrainingLogs((prev) => [...prev, ...lines]);
      }

      setTrainingLogs((prev) => [...prev, "✅ Training hoàn tất!"]);
    } catch (e) {
      setTrainingLogs([`❌ Lỗi: ${(e as Error).message}`]);
    }

    setIsTraining(false);
  };

  /* ======================
     UPDATE CONFIG
     ====================== */
  const handleConfigChange = (key: keyof TrainingConfig, value: number) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  /* ======================
     SAVE CONFIG
     ====================== */
  const handleSaveConfig = async () => {
    setConfigSaveStatus("⏳ Đang lưu...");

    try {
      const res = await fetch(`${API_BASE}/api/training/save-config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });

      if (res.ok) {
        setConfigSaveStatus("✅ Cấu hình đã lưu thành công!");
        setTimeout(() => setConfigSaveStatus(""), 3000);
      } else {
        setConfigSaveStatus("❌ Lưu cấu hình thất bại");
      }
    } catch (e) {
      setConfigSaveStatus(`❌ Lỗi: ${(e as Error).message}`);
    }
  };

  /* ======================
     COMPUTE DATA FOR CHARTS
     ====================== */
  const rocData =
    metrics?.roc_history.map((v, i) => ({
      epoch: i + 1,
      roc: v,
    })) ?? [];

  const histogramData = Array.from({ length: 20 }, (_, i) => {
    const min = i / 20;
    const max = (i + 1) / 20;
    return {
      bin: `${min.toFixed(2)}-${max.toFixed(2)}`,
      count: scores.filter((s) => s >= min && s < max).length,
    };
  });

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar username={username || "Admin"} isAdmin={true} />

      <div className="p-8">
        <h1 className="text-3xl font-bold mb-8">🛡️ Bảng điều khiển quản trị viên</h1>

        {/* TABS */}
        <div className="flex gap-4 mb-6">
        <button
          onClick={() => setActiveTab("upload")}
          className={`px-4 py-2 rounded flex items-center gap-2 transition ${
            activeTab === "upload"
              ? "bg-blue-600 text-white"
              : "bg-white border"
          }`}
        >
          <Upload size={16} /> Tải dữ liệu
        </button>
        <button
          onClick={() => setActiveTab("config")}
          className={`px-4 py-2 rounded flex items-center gap-2 transition ${
            activeTab === "config"
              ? "bg-blue-600 text-white"
              : "bg-white border"
          }`}
        >
          <Settings size={16} /> Cấu hình
        </button>
        <button
          onClick={() => setActiveTab("train")}
          className={`px-4 py-2 rounded flex items-center gap-2 transition ${
            activeTab === "train"
              ? "bg-blue-600 text-white"
              : "bg-white border"
          }`}
        >
          <Play size={16} /> Huấn luyện
        </button>
        <button
          onClick={() => setActiveTab("logs")}
          className={`px-4 py-2 rounded flex items-center gap-2 transition ${
            activeTab === "logs"
              ? "bg-blue-600 text-white"
              : "bg-white border"
          }`}
        >
          <FileText size={16} /> Nhật ký
        </button>
        <button
          onClick={() => setActiveTab("files")}
          className={`px-4 py-2 rounded flex items-center gap-2 transition ${
            activeTab === "files"
              ? "bg-blue-600 text-white"
              : "bg-white border"
          }`}
        >
          📂 File đã upload
        </button>
        </div>

        {/* CONTENT */}
      {/* TAB: UPLOAD TRAINING DATA */}
      {activeTab === "upload" && (
        <Card>
          <CardContent className="space-y-6">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <Upload size={24} /> Tải dữ liệu huấn luyện
            </h2>

            <div className="border-2 border-dashed rounded p-8 text-center">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setTrainingFile(e.target.files?.[0] || null)}
                className="hidden"
                id="training-file"
              />
              <label
                htmlFor="training-file"
                className="cursor-pointer block space-y-3"
              >
                <div className="text-4xl">📄</div>
                <p className="text-lg font-medium">
                  {trainingFile ? trainingFile.name : "Chọn file CSV"}
                </p>
                <p className="text-sm text-gray-500">
                  (Nhấp để chọn hoặc kéo thả file)
                </p>
              </label>
            </div>

            <Button
              className="w-full"
              onClick={handleUploadTrainingData}
              disabled={!trainingFile}
            >
              <Upload size={16} /> Tải lên
            </Button>

            {trainingStatus && (
              <div className="p-4 bg-blue-100 border border-blue-300 rounded text-blue-800">
                {trainingStatus}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* TAB: CONFIG */}
      {activeTab === "config" && (
        <Card>
          <CardContent className="space-y-6">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <Settings size={24} /> Cấu hình tham số huấn luyện
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* NITER */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Số epoch (niter)
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={config.niter}
                  onChange={(e) =>
                    handleConfigChange("niter", parseInt(e.target.value))
                  }
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              {/* LEARNING RATE */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Learning Rate (lr): {config.lr.toFixed(6)}
                </label>
                <input
                  type="number"
                  step="0.0001"
                  min="0.00001"
                  max="0.001"
                  value={config.lr}
                  onChange={(e) =>
                    handleConfigChange("lr", parseFloat(e.target.value))
                  }
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              {/* BETA1 */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Beta1
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={config.beta1}
                  onChange={(e) =>
                    handleConfigChange("beta1", parseFloat(e.target.value))
                  }
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              {/* W_ADV */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  W_ADV (Adversarial weight): {config.w_adv}
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={config.w_adv}
                  onChange={(e) =>
                    handleConfigChange("w_adv", parseFloat(e.target.value))
                  }
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              {/* W_CON */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  W_CON (Content weight): {config.w_con}
                </label>
                <input
                  type="number"
                  min="0"
                  max="200"
                  value={config.w_con}
                  onChange={(e) =>
                    handleConfigChange("w_con", parseFloat(e.target.value))
                  }
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              {/* W_ENC */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  W_ENC (Encoder weight): {config.w_enc}
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={config.w_enc}
                  onChange={(e) =>
                    handleConfigChange("w_enc", parseFloat(e.target.value))
                  }
                  className="w-full border rounded px-3 py-2"
                />
              </div>
            </div>

            <div className="p-4 bg-gray-100 rounded text-sm">
              <p className="font-semibold mb-2">📝 Cấu hình hiện tại:</p>
              <code>{JSON.stringify(config, null, 2)}</code>
            </div>

            <Button className="w-full" onClick={handleSaveConfig}>
              💾 Lưu cấu hình
            </Button>

            {configSaveStatus && (
              <div className={`p-4 rounded text-center ${
                configSaveStatus.includes("✅")
                  ? "bg-green-100 border border-green-300 text-green-800"
                  : "bg-red-100 border border-red-300 text-red-800"
              }`}>
                {configSaveStatus}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* TAB: TRAIN */}
      {activeTab === "train" && (
        <div className="space-y-6">
          {/* RUN TRAINING BUTTON */}
          <Card>
            <CardContent className="space-y-4">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <Play size={24} /> Huấn luyện mô hình
              </h2>

              <Button
                className="w-full"
                onClick={handleRunTraining}
                disabled={isTraining}
              >
                <TrendingUp size={16} />{" "}
                {isTraining ? "⏳ Đang huấn luyện..." : "🚀 Bắt đầu huấn luyện"}
              </Button>

              <div className="h-96 bg-black text-green-400 font-mono text-xs p-4 overflow-y-auto rounded border">
                {trainingLogs.length === 0
                  ? "Nhấn nút trên để bắt đầu huấn luyện...\n"
                  : trainingLogs.map((log, i) => <div key={i}>{log}</div>)}
              </div>
            </CardContent>
          </Card>

          {/* METRICS */}
          <Card>
            <CardContent>
              <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                📊 Chỉ số đánh giá
              </h2>

              {/* KPI */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <Card>
                  <CardContent>
                    <p className="text-sm">ROC AUC</p>
                    <p className="text-2xl font-bold">
                      {metrics ? metrics.roc_auc.toFixed(3) : "--"}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent>
                    <p className="text-sm">Thời gian chạy trung bình (ms/batch)</p>
                    <p className="text-2xl font-bold">
                      {metrics ? metrics.avg_runtime_ms.toFixed(2) : "--"}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* CHARTS */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* ROC CURVE */}
                <div>
                  <p className="text-sm font-semibold mb-2 flex items-center gap-2">
                    <BarChart3 size={14} /> Đường cong ROC
                  </p>
                  <div className="h-48 bg-white border rounded">
                    {metrics ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={rocData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="epoch" />
                          <YAxis domain={[0, 1]} />
                          <Tooltip />
                          <Line
                            type="monotone"
                            dataKey="roc"
                            stroke="#2563eb"
                            strokeWidth={2}
                            dot={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-400">
                        Chưa có dữ liệu
                      </div>
                    )}
                  </div>
                </div>

                {/* CONFUSION MATRIX */}
                <div>
                  <p className="text-sm font-semibold mb-2 flex items-center gap-2">
                    <Grid size={14} /> Ma trận nhầm lẫn
                  </p>
                  <div className="h-48 bg-white border rounded p-4">
                    {confusion ? (
                      <table className="w-full h-full text-center border">
                        <tbody>
                          <tr>
                            <td className="border bg-green-100">
                              TN<br />{confusion.tn}
                            </td>
                            <td className="border bg-red-100">
                              FP<br />{confusion.fp}
                            </td>
                          </tr>
                          <tr>
                            <td className="border bg-red-100">
                              FN<br />{confusion.fn}
                            </td>
                            <td className="border bg-green-100">
                              TP<br />{confusion.tp}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-400">
                        Chưa có dữ liệu
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* HISTOGRAM */}
              <div className="mt-4">
                <p className="text-sm font-semibold mb-2">
                  Phân bố điểm bất thường
                </p>
                <div className="h-40 bg-white border rounded">
                  {scores.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={histogramData}>
                        <XAxis dataKey="bin" hide />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#2563eb" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-full flex items-center justify-center text-gray-400">
                      Chưa có dữ liệu
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* TAB: LOGS */}
      {activeTab === "logs" && (
        <Card>
          <CardContent className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <FileText size={24} /> Nhật ký kiểm tra bất thường
              </h2>
              <Button onClick={loadInferenceLogs} disabled={loadingLogs}>
                {loadingLogs ? "⏳ Đang tải..." : "🔄 Làm mới"}
              </Button>
            </div>

            {inferenceLogs.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <p>Chưa có nhật ký nào</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border">
                  <thead>
                    <tr className="bg-gray-200">
                      <th className="border p-2 text-left">File CSV</th>
                      <th className="border p-2 text-center">Tổng mẫu</th>
                      <th className="border p-2 text-center">Bình thường</th>
                      <th className="border p-2 text-center">Bất thường</th>
                      <th className="border p-2 text-center">% Bất thường</th>
                      <th className="border p-2 text-left">Thời gian</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inferenceLogs.map((log) => (
                      <tr key={log.log_id} className="hover:bg-gray-50">
                        <td className="border p-2 font-mono text-sm">
                          {log.csv_filename}
                        </td>
                        <td className="border p-2 text-center">
                          {log.total_samples}
                        </td>
                        <td className="border p-2 text-center text-green-600 font-medium">
                          {log.normal_count}
                        </td>
                        <td className="border p-2 text-center text-red-600 font-medium">
                          {log.anomaly_count}
                        </td>
                        <td className="border p-2 text-center">
                          {log.anomaly_percentage.toFixed(2)}%
                        </td>
                        <td className="border p-2 text-sm text-gray-600">
                          {new Date(log.created_at).toLocaleString("vi-VN")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* TAB: UPLOADED FILES */}
      {activeTab === "files" && (
        <Card>
          <CardContent className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                📂 Danh sách file đã upload
              </h2>
              <Button onClick={loadUploadedFiles} disabled={loadingFiles}>
                {loadingFiles ? "⏳ Đang tải..." : "🔄 Làm mới"}
              </Button>
            </div>

            {uploadedFiles.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <p>Chưa có file nào được upload</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border">
                  <thead>
                    <tr className="bg-gray-200">
                      <th className="border p-2 text-left">Tên file</th>
                      <th className="border p-2 text-center">Số mẫu</th>
                      <th className="border p-2 text-center">Số đặc trưng</th>
                      <th className="border p-2 text-left">Ngày tải</th>
                    </tr>
                  </thead>
                  <tbody>
                    {uploadedFiles.map((file) => (
                      <tr key={file.upload_id} className="hover:bg-gray-50">
                        <td className="border p-2 font-mono text-sm">
                          {file.filename}
                        </td>
                        <td className="border p-2 text-center">
                          {file.num_rows}
                        </td>
                        <td className="border p-2 text-center">
                          {file.num_features}
                        </td>
                        <td className="border p-2 text-sm text-gray-600">
                          {new Date(file.created_at).toLocaleString("vi-VN")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
        </div>
    </div>
  );
}

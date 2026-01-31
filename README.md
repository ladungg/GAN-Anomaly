# 🤖 GAN Anomaly Detection System

Hệ thống phát hiện bất thường mạng máy tính sử dụng GAN (Generative Adversarial Network) với dữ liệu NSL-KDD.

**Model**: GANAnomaly  
**Dataset**: NSL-KDD (44 cột → 116 features sau xử lý)  
**ROC Score**: 0.93-0.97  
**Threshold**: 0.985 (tối ưu)

---

## 🚀 Chuẩn bị

### Yêu cầu hệ thống
- Python 3.8+
- Node.js 18+
- npm hoặc yarn

### Cài đặt

#### 1. Clone hoặc tải project
```bash
cd c:\Users\Desktop\GAN
```

#### 2. Backend - Python
```bash
cd backend

# Cài đặt thư viện
pip install -r requirements.txt

# Hoặc cài từng cái:
pip install fastapi uvicorn sqlite3 pandas numpy scikit-learn torch torchvision
```

#### 3. Frontend - Node.js
```bash
cd frontend

# Cài đặt dependencies
npm install
```

---

## ▶️ Chạy hệ thống

### Backend (FastAPI)
```bash
cd backend
python main.py
```
✅ Server chạy tại: `http://127.0.0.1:8000`

**API Docs**: `http://127.0.0.1:8000/docs`

### Frontend (React + Vite)
```bash
cd frontend
npm run dev
```
✅ Server chạy tại: `http://localhost:5174` (hoặc port khác nếu 5173-5174 bị dùng)

---

## 📁 Cấu trúc folder

```
GAN/
├── backend/
│   ├── main.py              # Entry point backend
│   ├── requirements.txt      # Dependencies Python
│   ├── app/
│   │   ├── controllers/      # Xử lý logic API
│   │   ├── services/         # Business logic (inference, CSV)
│   │   ├── routes/           # API endpoints
│   │   ├── models/           # Database & ORM
│   │   └── utils/            # Utilities
│   ├── uploads/              # Folder chứa CSV tải lên
│   └── results/              # Folder chứa CSV kết quả
│
├── frontend/
│   ├── src/
│   │   ├── pages/            # Trang chính (Login, Dashboard)
│   │   ├── components/       # Các component UI
│   │   └── main.tsx          # Entry point
│   ├── package.json          # Dependencies Node.js
│   └── vite.config.ts        # Config Vite
│
└── GANAnomaly/               # Thư viện GAN training
    ├── train.py              # Script train model
    ├── config_training.json   # Config training (epochs, etc)
    └── output/               # Weights model (netG.pth, netD.pth)
```

---

## 🔄 Workflow sử dụng

### 1. **Login**
- Username: `admin` hoặc `user`
- Password: `password123`

### 2. **Upload CSV để kiểm tra**
- File format: CSV với 116 features (NSL-KDD preprocessed)
- CSV sẽ được lưu vào `backend/uploads/`

### 3. **Chạy Inference**
- Backend tự động:
  1. Đọc CSV
  2. Chuẩn bị dữ liệu (preprocess nếu cần)
  3. Chạy GAN inference
  4. Phân loại: NORMAL (D_output ≥ 0.985) / ATTACK (D_output < 0.985)
  5. Lưu kết quả vào `backend/results/`

### 4. **Tải kết quả**
- Click "⬇️ Tải file kết quả (CSV có đánh dấu)"
- CSV sẽ có cột `prediction_status` với giá trị NORMAL/ATTACK
- Frontend sẽ tô màu đỏ cho dòng ATTACK

### 5. **Xem lịch sử**
- Tất cả lần kiểm tra được lưu ở localStorage
- Reload trang vẫn giữ lịch sử
- Có nút "🗑️ Xóa lịch sử" để clear

---

## 🧪 Test

### Clear Database
Xóa dữ liệu logs, uploads (giữ user table):
```bash
cd backend
python clear_database.py
```

---

## 📊 Database

**Vị trí**: `backend/app/models/anomaly_detection.db` (SQLite)

**Bảng chính**:
| Bảng | Mô tả |
|------|-------|
| `users` | Tài khoản người dùng |
| `csv_uploads` | Lịch sử upload files |
| `predictions` | Kết quả dự đoán từng row |
| `inference_logs` | Summary log từng lần inference |

---

## 🔧 Troubleshooting

### Backend không chạy
```bash
# Check port 8000 có bị dùng không
netstat -ano | findstr :8000

# Nếu cần, kill process đó hoặc đổi port trong main.py
```

### Frontend không load
```bash
# Xóa cache node_modules, reinstall
cd frontend
Remove-Item node_modules -Recurse
npm install
npm run dev
```

### Database error
```bash
# Reset database (giữ users)
cd backend
python clear_database.py
```

### Model file không tìm thấy
```bash
# Kiểm tra weights model
# Cần có: GANAnomaly/output/FlowGANAnomaly/nsl/train/weights/
# - netG.pth
# - netD.pth
```

---

## 📝 Logs

**Backend logs**: In ra console khi chạy `python main.py`

**Frontend logs**: Browser console (F12 → Console tab)

**Database logs**: `backend/app/models/anomaly_detection.db`

---

## 🎯 Key Features

✅ Upload CSV file tùy ý  
✅ Tự động preprocess dữ liệu (pad/truncate về 116 features)  
✅ Inference real-time với GAN model  
✅ Tải kết quả CSV có đánh dấu NORMAL/ATTACK  
✅ Lưu lịch sử kiểm tra (localStorage)  
✅ Dashboard với metrics, confusion matrix  

---

## 📞 Support

Nếu gặp lỗi:
1. Check backend logs
2. Check browser console
3. Restart backend + frontend
4. Clear database nếu cần reset

---

**Last Updated**: 31/1/2026  
**Status**: Production Ready ✅

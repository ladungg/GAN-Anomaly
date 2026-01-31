# Admin Panel & Training Features - Implementation Guide

## 📋 Các tính năng đã thêm

### 1. **Admin Panel Page** (`/admin`)
Giao diện quản trị viên với 4 tab chính:

#### Tab 1: Tải dữ liệu huấn luyện (Upload Training Data)
- Tải lên file CSV chứa dữ liệu huấn luyện mới
- Endpoint: `POST /api/v1/training/upload-data`
- Yêu cầu: File CSV có format dạng `num_rows × num_features`

#### Tab 2: Cấu hình tham số (Config Parameters)
- Điều chỉnh tham số huấn luyện qua giao diện
- Các tham số có thể điều chỉnh:
  - `niter`: Số epoch (1-20)
  - `lr`: Learning rate (0.00001 - 0.001)
  - `beta1`: Adam optimizer beta1 (0-1)
  - `w_adv`: Adversarial loss weight (0-100)
  - `w_con`: Content loss weight (0-200)
  - `w_enc`: Encoder loss weight (0-100)

#### Tab 3: Huấn luyện mô hình (Train Model)
- Bắt đầu huấn luyện với config đã cấu hình
- Endpoint: `POST /api/v1/training/train`
- Hiển thị log realtime stream
- Support streaming output từ training process

#### Tab 4: Xem nhật ký (View Inference Logs)
- Hiển thị danh sách các lần user kiểm tra tấn công/bình thường
- Endpoint: `GET /api/v1/inference/logs`
- Thông tin:
  - Tên file CSV
  - Tổng số mẫu
  - Số mẫu bình thường
  - Số mẫu bất thường
  - Tỷ lệ % bất thường
  - Thời gian chạy

---

## 🔌 API Endpoints (Backend)

### Training API
```
POST /api/v1/training/upload-data
- Content-Type: multipart/form-data
- Body: file (CSV)
- Response: {status, filename, num_rows, num_features}

POST /api/v1/training/train
- Content-Type: application/json
- Body: {niter, lr, beta1, w_adv, w_con, w_enc}
- Response: Streaming logs (text/plain)
```

### Authentication API
```
POST /api/v1/auth/register
- Body: {username, email, password}

POST /api/v1/auth/login
- Body: {username, password}
- Response: {access_token, role}
```

---

## 🔐 Role-based Routing

Login endpoint giờ trả về `role` field:
- `role: "admin"` → Redirect tới `/admin`
- `role: "user"` hoặc không có → Redirect tới `/dashboard`

---

## 📁 File Structure

### Frontend
```
src/
├── pages/
│   ├── Admin.tsx          (NEW) - Admin dashboard
│   ├── Login.tsx          (UPDATED) - Role-based redirect
│   ├── Register.tsx       (UPDATED) - API path fix
│   └── Dashboard.tsx      (UPDATED) - Add Navbar
├── components/
│   ├── Navbar.tsx         (NEW) - Navigation bar
│   ├── Button.tsx
│   ├── Card.tsx
│   └── PageHeader.tsx
└── App.tsx               (UPDATED) - Enable routing
```

### Backend
```
app/
├── routes/v1/
│   ├── auth.py
│   ├── training.py       (UPDATED) - Add upload-data, train endpoints
│   ├── inference.py
│   └── config.py
├── controllers/
│   └── training_controller.py  (UPDATED) - Add upload & config functions
├── services/
│   ├── training_data_manager.py (NEW) - Handle training data
│   ├── inference_engine.py
│   └── logging_service.py
└── models/
    └── database.py       (users table với role field)
```

---

## 🚀 Cách sử dụng Admin Panel

### 1. Đăng nhập với tài khoản admin
```
Username: admin
Password: admin123
```

### 2. Upload dữ liệu huấn luyện
- Vào tab "Tải dữ liệu"
- Chọn file CSV
- Nhấn "Tải lên"

### 3. Cấu hình tham số
- Vào tab "Cấu hình"
- Điều chỉnh các slider/input
- Nhấn "Bắt đầu huấn luyện" sẽ dùng config này

### 4. Huấn luyện
- Vào tab "Huấn luyện"
- Nhấn "Bắt đầu huấn luyện"
- Xem log realtime

### 5. Xem nhật ký
- Vào tab "Nhật ký"
- Xem bảng các inference logs
- Thông tin: filename, total samples, normal/anomaly count, %

---

## ⚙️ Configuration

### User Roles (Database)
```sql
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT DEFAULT 'user',  -- 'admin' hoặc 'user'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME
);
```

### Training Data Storage
```
training_data/          ← Thư mục lưu training files
├── data_1.csv
├── data_2.csv
└── ...
```

---

## 📊 API Response Examples

### Login Response
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "username": "admin",
  "role": "admin"
}
```

### Inference Logs Response
```json
{
  "logs": [
    {
      "log_id": 1,
      "csv_filename": "test_data.csv",
      "total_samples": 100,
      "normal_count": 80,
      "anomaly_count": 20,
      "anomaly_percentage": 20.0,
      "created_at": "2026-01-28T10:30:00"
    },
    ...
  ]
}
```

---

## ✅ Testing Checklist

- [ ] Login với admin account → Should redirect to /admin
- [ ] Login với user account → Should redirect to /dashboard
- [ ] Upload CSV training data → Should show filename & stats
- [ ] Adjust config parameters → Should update slider values
- [ ] Start training → Should stream logs
- [ ] View inference logs → Should show table with data
- [ ] Navbar shows correct username
- [ ] Navbar shows "Admin" link for admin users
- [ ] Logout button works → Should redirect to login

---

## 🔧 Development Notes

1. **Token Decoding**: Frontend decodes JWT token để lấy username & role
2. **Streaming Logs**: Training logs được stream realtime từ backend
3. **Role-based UI**: Navbar thêm link Admin chỉ cho admin users
4. **Inference Logs**: Tự động populated bởi inference_service khi user chạy predict
5. **Training Config**: Saved vào `config_training.json` rồi pass tới train script

---

## 🎯 Next Steps

1. ✅ Implement Admin Panel UI
2. ✅ Add Training API endpoints
3. ✅ Add Navbar component
4. ⏳ Test authentication & routing
5. ⏳ Test training upload & execution
6. ⏳ Test inference logs display

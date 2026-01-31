# GAN Anomaly Detection Backend

## Cấu trúc MVC

```
app/
├── models/          # M - Database & Data Models
├── controllers/     # C - Business Logic
├── routes/          # V - API Routes/Endpoints
├── services/        # Utility/Helper Functions
└── utils/           # Constants & Configurations
```

## Cách dùng

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Khởi tạo database:**
```bash
python -m app.models.init_db
```

3. **Chạy backend:**
```bash
uvicorn main:app --reload
```

Hoặc:
```bash
python main.py
```

## API Endpoints

### Authentication (`/api/auth/*`)
- `POST /api/auth/login` - Đăng nhập
  - Request: `{username, password}`
  - Response: `{status, message, access_token, user_id, username, email, role, created_at}`
  
- `POST /api/auth/register` - Đăng ký tài khoản mới
  - Request: `{username, email, password}`
  - Response: `{status, message, user_id, username, email}`

- `GET /api/auth/user/{user_id}` - Lấy thông tin người dùng
  - Response: `{status, user: {...}}`

### Training (`/api/training/*`)
- `POST /api/training/upload-data` - Tải dữ liệu huấn luyện
  - Body: FormData với file CSV
  - Response: `{status, message, num_rows, num_features}`

- `POST /api/training/train` - Bắt đầu huấn luyện mô hình
  - Request: `{niter, lr, beta1, w_adv, w_con, w_enc}`
  - Response: Stream log training

- `POST /api/training/save-config` - Lưu cấu hình tham số
  - Request: `{niter, lr, beta1, w_adv, w_con, w_enc}`
  - Response: `{status, message}`

### Inference (`/api/inference/*`)
- `POST /api/inference/predict` - Dự đoán bất thường trên file CSV
  - Body: FormData với file CSV
  - Response: `{status, total, normal, attack, normal_percentage, attack_percentage}`

- `GET /api/inference/logs` - Lấy nhật ký kiểm tra bất thường
  - Response: `{logs: [{log_id, csv_filename, total_samples, normal_count, anomaly_count, anomaly_percentage, created_at}, ...]}`

- `GET /api/inference/uploads` - Lấy danh sách file đã upload
  - Response: `{uploads: [{upload_id, filename, num_rows, num_features, created_at}, ...]}`

### Metrics (`/api/metrics/*`)
- `GET /api/metrics` - Lấy training metrics
  - Response: `{roc_auc, avg_runtime_ms, max_roc, roc_history: [...]}`

- `GET /api/confusion-matrix` - Lấy confusion matrix
  - Response: `{matrix: [[tn, fp], [fn, tp]], tn, fp, fn, tp}`

- `GET /api/anomaly-scores` - Lấy anomaly scores
  - Response: `{scores: [...]}`

## Default Credentials

- **Admin**: username: `admin`, password: `admin123`
- **User**: username: `user`, password: `user123`
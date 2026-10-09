# Configuration Guide: Beyond Synthetic Missingness

Tài liệu này hướng dẫn cách cấu hình và truyền đường dẫn dữ liệu thô (raw dataset) cho toàn bộ pipeline nghiên cứu.

---

## 1. Nguyên tắc cốt lõi

1. **Tuyệt đối không hard-code đường dẫn vật lý** trong mã nguồn nghiên cứu (`etl/`, `models/`, `analysis/`, `masks/`).
2. **Hỗ trợ đường dẫn có khoảng trắng**: Toàn bộ module sử dụng `pathlib.Path` để đảm bảo tương thích tuyệt đối với các đường dẫn phân vùng ổ đĩa như `/run/media/.../New Volume/Vice - Download/Honda_Dataset`.
3. **READ-ONLY tuyệt đối**: Thư mục raw dataset từ nguồn ngoài chỉ được đọc (read-only), không di chuyển, không sao chép nguyên trạng vào repo và không chỉnh sửa.
4. **Bảo mật môi trường cục bộ**: File `configs/local.yaml` được đưa vào `.gitignore` để không bị commit lên git repo, tránh làm lộ đường dẫn máy cá nhân hoặc gây xung đột môi trường.

---

## 2. Các file cấu hình

| File | Mục đích | Theo dõi bởi Git? |
|---|---|:---:|
| `configs/default.yaml` | Cấu hình mặc định mẫu cho repository | Có |
| `configs/local.yaml.example` | Mẫu hướng dẫn tạo cấu hình cho máy cá nhân | Có |
| `configs/local.yaml` | Cấu hình thực tế trên máy hiện tại (chứa đường dẫn raw data ngoài) | **Không** (bị `.gitignore`) |

---

## 3. Cách cấu hình đường dẫn dữ liệu ngoài

Tạo hoặc chỉnh sửa file `configs/local.yaml`:

```yaml
protocol_version: "v1"

data:
  # Đường dẫn tới thư mục gốc bộ dữ liệu Honda Smart Meter
  raw_dir: "/run/media/duck/New Volume/Vice - Download/Honda_Dataset"
  interim_dir: "data/interim"
  processed_dir: "data/processed"

experiment:
  seed: 42
  timezone: "UTC"
  target_resolution: "15min"
```

---

## 4. Cách sử dụng trong mã nguồn Python

Mọi script nghiên cứu đều nạp cấu hình qua `src.config` hoặc `etl.config`:

```python
from src.config import load_config, get_raw_data_dir, validate_honda_dataset

# 1. Tự động nhận qua CLI flag --config <path>, hoặc fallback về local.yaml / default.yaml
config = load_config()

# 2. Lấy đường dẫn Path an toàn (hỗ trợ khoảng trắng, kiểm tra tồn tại và quyền đọc)
raw_dir = get_raw_data_dir(config)
print("Thư mục raw data:", raw_dir)

# 3. Kiểm tra tính hợp lệ của cấu trúc Honda dataset (81 meters, issues...)
dataset_info = validate_honda_dataset(raw_dir)
print(f"Tổng số meter hợp lệ: {dataset_info['meter_count']}")
```

---

## 5. Chạy từ dòng lệnh (CLI)

Chạy kiểm tra cấu hình:
```bash
# Kiểm tra tự động với local.yaml mặc định
python3 -m src.config

# Chỉ định rõ file cấu hình bất kỳ
python3 -m src.config --config configs/local.yaml

# Xác thực chi tiết cấu trúc dataset Honda
python3 -m src.config --config configs/local.yaml --validate
```

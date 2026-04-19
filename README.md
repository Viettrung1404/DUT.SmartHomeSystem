# Smart Home - Docker Setup

Dự án Smart Home với backend (FastAPI + PostgreSQL) và mobile (React Native/Expo) chạy trong Docker.

## Cấu trúc

- `Dockerfile.backend` - Dockerfile cho backend API
- `Dockerfile.mobile` - Dockerfile cho Expo dev server
- `docker-compose.yml` - Orchestration cho tất cả services

## Cách sử dụng

### Khởi động tất cả services

```bash
docker-compose up
```

Hoặc chạy ở chế độ background:

```bash
docker-compose up -d
```

### Khởi động từng service riêng lẻ

```bash
# Chỉ backend + database
docker-compose up backend db

# Chỉ mobile
docker-compose up mobile
```

### Xem logs

```bash
# Tất cả services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Mobile only
docker-compose logs -f mobile
```

### Dừng services

```bash
docker-compose down
```

### Rebuild images

```bash
docker-compose up --build
```

## Services

### Backend API

- **Port**: 8000
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

### PostgreSQL Database

- **Port**: 5433 (host) -> 5432 (container)
- **Database**: smarthome
- **User**: postgres
- **Password**: postgres

### Mobile (Expo Dev Server)

- **Metro Bundler**: http://localhost:8081
- **Expo DevTools**: http://localhost:19000
- **iOS**: http://localhost:19001
- **Android**: http://localhost:19002

## Kết nối Mobile với Backend

Khi chạy trong Docker, mobile app có thể kết nối tới backend qua:

- `http://backend:8000` (từ trong container network)
- `http://localhost:8000` (từ máy host)

## Lưu ý

- Tất cả services chạy trong cùng network `app-network` nên có thể giao tiếp với nhau
- Volume mount giúp hot-reload khi code thay đổi
- PostgreSQL data được lưu trong volume `postgres_data` nên không mất khi restart

## Troubleshooting

### Port đã được sử dụng

Thay đổi port mapping trong `docker-compose.yml` nếu port bị conflict.

### Mobile app không kết nối được backend

Kiểm tra network settings và đảm bảo backend đã chạy thành công.
pkill -f device_client.py
pkill -f face_client.py

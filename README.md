# Starter API — Python

REST API starter template menggunakan **FastAPI + SQLAlchemy 2.0 + Pydantic v2**, mendukung MySQL, PostgreSQL, SQLite, dan SQL Server.

## Fitur

- JWT Authentication (access + refresh token, disimpan di DB)
- Google & Facebook OAuth (raw HTTP via httpx, tanpa SDK)
- Role & Permission (category → menu → action)
- `is_root` bypass semua permission
- Soft delete, UUID primary key
- Ganti password, lupa password (email link)
- Upload foto profil (max 2MB, JPEG/PNG/WebP)
- Multi-database: MySQL, PostgreSQL, SQLite, SQL Server
- Auto-generate tabel via SQLAlchemy `create_all`

## Struktur Direktori

```
python/
├── app/
│   ├── schemas/          # Pydantic v2 request schema
│   ├── services/         # Business logic (auth, user, role, permission)
│   ├── routers/          # FastAPI router
│   ├── config.py         # Settings dari .env
│   ├── database.py       # SQLAlchemy engine + session
│   ├── deps.py           # Dependency injection (auth, permission)
│   ├── mail.py           # SMTP mailer (smtplib)
│   ├── models.py         # SQLAlchemy ORM model
│   ├── response.py       # JSONResponse helper
│   ├── security.py       # JWT + bcrypt
│   ├── serializers.py    # ORM → dict serializer
│   └── seeder.py         # Seeder permission tree + root user
├── storage/photos/       # Foto yang di-upload
├── main.py               # Entry point FastAPI
├── .env.example
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Persyaratan

- Python 3.11+
- pip
- Database: MySQL 8+ / PostgreSQL 14+ / SQLite / SQL Server

---

## Menjalankan Lokal (Development)

### 1. Setup environment

```bash
cp .env.example .env
# Edit .env sesuai konfigurasi lokal Anda
```

### 2. Buat virtual environment & install dependensi

```bash
python -m venv venv

# Aktivasi (Linux/Mac)
source venv/bin/activate

# Aktivasi (Windows)
venv\Scripts\activate

pip install -r requirements.txt
# Atau: make install
```

### 3. Jalankan server

```bash
# Development (hot reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Atau: make dev

# Production-like
uvicorn main:app --host 0.0.0.0 --port 8000
# Atau: make run

# Via python langsung
python main.py
# Atau: make start
```

Server berjalan di `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

### Environment Variables

| Variable | Default | Keterangan |
|---|---|---|
| `APP_PORT` | `8000` | Port server |
| `APP_URL` | `http://localhost:8000` | Base URL |
| `DB_DRIVER` | `mysql` | `mysql` / `postgres` / `sqlite` / `mssql` |
| `DB_HOST` | `127.0.0.1` | Host database |
| `DB_PORT` | `3306` | Port database |
| `DB_USER` | `root` | Username database |
| `DB_PASS` | _(kosong)_ | Password database |
| `DB_NAME` | `fid_starter_api` | Nama database |
| `JWT_SECRET` | `secret` | Secret key JWT |
| `JWT_ACCESS_EXPIRE` | `15` | Expire access token (menit) |
| `JWT_REFRESH_EXPIRE` | `10080` | Expire refresh token (menit) |
| `EMAIL_VERIFICATION_REQUIRED` | `false` | Wajib verifikasi email |
| `MAIL_HOST` | _(kosong)_ | SMTP host |
| `MAIL_PORT` | `587` | SMTP port |
| `MAIL_USER` | _(kosong)_ | SMTP username |
| `MAIL_PASS` | _(kosong)_ | SMTP password |
| `MAIL_FROM` | `no-reply@example.com` | Alamat pengirim |
| `GOOGLE_CLIENT_ID` | _(kosong)_ | Google OAuth client ID |
| `FACEBOOK_CLIENT_ID` | _(kosong)_ | Facebook OAuth client ID |
| `STORAGE_PATH` | `./storage/photos` | Direktori foto |

### Akun Default (setelah seeder)

| Field | Value |
|---|---|
| Email | `root@example.com` |
| Password | `password` |

---

## Deploy ke VPS (Production)

### 1. Setup di VPS

```bash
ssh user@your-vps

# Install Python
sudo apt update && sudo apt install -y python3.12 python3.12-venv python3-pip

# Siapkan direktori
mkdir -p /opt/starter-api-python
cd /opt/starter-api-python
```

### 2. Upload & install

```bash
# Di mesin lokal
rsync -avz --exclude=venv --exclude=__pycache__ --exclude=storage \
  ./ user@your-vps:/opt/starter-api-python/

# Di VPS
cd /opt/starter-api-python
cp .env.production .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p storage/photos
```

### 3. Buat systemd service

```bash
sudo nano /etc/systemd/system/starter-api-python.service
```

```ini
[Unit]
Description=Starter API Python FastAPI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/starter-api-python
ExecStart=/opt/starter-api-python/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
EnvironmentFile=/opt/starter-api-python/.env
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable starter-api-python
sudo systemctl start starter-api-python
sudo systemctl status starter-api-python
```

### 4. Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name api.example.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /storage/photos/ {
        alias /opt/starter-api-python/storage/photos/;
        expires 30d;
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.example.com
```

---

## Deploy dengan Docker

### 1. Build image

```bash
docker build -t starter-api-python .
```

### 2. Jalankan container

```bash
docker run -d \
  --name starter-api-python \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/storage:/app/storage \
  --restart unless-stopped \
  starter-api-python
```

### 3. Menggunakan Docker Compose

```yaml
version: "3.9"

services:
  api:
    build: .
    container_name: starter-api-python
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./storage:/app/storage
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: mysql:8.0
    container_name: fid-starter-api-db
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: fid_starter_api
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  db_data:
```

```bash
# Set DB_HOST=db di .env
docker compose up -d
docker compose logs -f api
```

---

## API Endpoints

| Method | Endpoint | Auth | Keterangan |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | Register |
| POST | `/api/v1/auth/login` | — | Login |
| POST | `/api/v1/auth/logout` | ✓ | Logout |
| POST | `/api/v1/auth/refresh` | — | Refresh token |
| POST | `/api/v1/auth/revoke` | — | Revoke token |
| POST | `/api/v1/auth/forgot-password` | — | Kirim link reset |
| POST | `/api/v1/auth/reset-password` | — | Reset password |
| GET | `/api/v1/auth/verify-email?token=` | — | Verifikasi email |
| POST | `/api/v1/auth/change-password` | ✓ | Ganti password |
| GET | `/api/v1/auth/me` | ✓ | Profil sendiri |
| PUT | `/api/v1/profile` | ✓ | Update profil |
| POST | `/api/v1/profile/photo` | ✓ | Upload foto |
| POST | `/api/v1/auth/oauth/google` | — | Login Google |
| POST | `/api/v1/auth/oauth/facebook` | — | Login Facebook |
| GET | `/api/v1/users` | ✓ `user:index` | Daftar user |
| POST | `/api/v1/users` | ✓ `user:create` | Buat user |
| GET | `/api/v1/users/{id}` | ✓ `user:show` | Detail user |
| PUT | `/api/v1/users/{id}` | ✓ `user:edit` | Update user |
| DELETE | `/api/v1/users/{id}` | ✓ `user:delete` | Hapus user |
| POST | `/api/v1/users/{id}/photo` | ✓ `user:edit` | Upload foto user |
| GET | `/api/v1/roles` | ✓ `role:index` | Daftar role |
| POST | `/api/v1/roles` | ✓ `role:create` | Buat role |
| GET | `/api/v1/roles/{id}` | ✓ `role:show` | Detail role |
| PUT | `/api/v1/roles/{id}` | ✓ `role:edit` | Update role |
| DELETE | `/api/v1/roles/{id}` | ✓ `role:delete` | Hapus role |
| GET | `/api/v1/permissions` | ✓ `permission:index` | Daftar permission |
| GET | `/api/v1/permissions/tree` | ✓ `permission:index` | Tree permission |
| GET | `/api/v1/permissions/by-role/{id}` | ✓ `permission:index` | Permission by role |

## Format Response

```json
{
  "success": true,
  "message": "Data retrieved",
  "data": {},
  "meta": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "total_page": 10
  }
}
```

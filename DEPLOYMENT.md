# Deployment Guide - Parking Management System

## Production Deployment

This guide covers deploying the Parking Management application to production.

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (for containerized deployment)
- Environment variables configured in `.env` file

### Environment Setup

1. **Create `.env` file from template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure required variables:**
   - `SECRET_KEY`: Generate a strong secret key
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - `MAIL_USERNAME` & `MAIL_PASSWORD`: Gmail SMTP credentials
   - `RAZORPAY_KEY_ID` & `RAZORPAY_KEY_SECRET`: Razorpay API credentials (optional for demo mode)

### Deployment Options

#### Option 1: Docker Deployment (Recommended)

**Build image:**
```bash
docker build -t parking-management:latest .
```

**Run container:**
```bash
docker run -d \
  --name parking-app \
  -p 5000:5000 \
  --env-file .env \
  -v parking_db:/app/data \
  parking-management:latest
```

**Using Docker Compose:**
```bash
docker-compose up -d
```

#### Option 2: Traditional Deployment

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Initialize database:**
```bash
python init_db.py
```

**3. Run with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 wsgi:app
```

For production with more workers:
```bash
gunicorn -w 8 --worker-class sync -b 0.0.0.0:5000 \
  --access-logfile - --error-logfile - \
  --log-level info wsgi:app
```

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure email credentials
- [ ] Set up database backups
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure firewall rules
- [ ] Test health endpoint: `GET /health`

### Monitoring

**Health Check:**
```bash
curl http://localhost:5000/health
```

**View Logs:**
```bash
tail -f logs/parking_app.log
```

### Performance Tuning

**Gunicorn Workers Formula:**
- Threads/Workers = (2 × CPU cores) + 1
- For 2-core system: 5 workers
- For 4-core system: 9 workers

**Example for 4-core production:**
```bash
gunicorn -w 9 --worker-class sync -b 0.0.0.0:5000 wsgi:app
```

### Database Backups

**Backup SQLite database:**
```bash
cp parking.db parking.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Reverse Proxy Setup (Nginx)

```nginx
upstream parking_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://parking_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        access_log off;
        proxy_pass http://parking_app;
    }
}
```

### Troubleshooting

**Port already in use:**
```bash
lsof -i :5000
kill -9 <PID>
```

**Database locked error:**
Ensure only one process is writing to the database at a time.

**Email not sending:**
- Verify MAIL_USERNAME and MAIL_PASSWORD
- Check firewall allows port 587
- Ensure "Less secure app access" is enabled (Gmail)

### Security Notes

- Always use HTTPS in production
- Rotate `SECRET_KEY` periodically
- Keep dependencies updated
- Use strong database passwords
- Enable rate limiting on public endpoints
- Monitor logs for suspicious activity

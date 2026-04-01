# Production Deployment Scripts

## Quick Start

### Development Mode
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Run development server
python app.py
```

### Production Mode (Docker)
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop
docker-compose down
```

### Production Mode (Traditional)
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Key Files

- `wsgi.py` - WSGI entry point for production servers
- `.env.example` - Environment variables template
- `Dockerfile` - Container definition
- `docker-compose.yml` - Multi-container orchestration
- `DEPLOYMENT.md` - Detailed deployment guide

## Health Check

```bash
curl http://localhost:5000/health
# Response: {"status": "healthy"}
```

## Logs Location

- Docker: `docker-compose logs web`
- Traditional: `logs/parking_app.log`

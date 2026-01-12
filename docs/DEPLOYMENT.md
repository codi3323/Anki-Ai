# Deployment Guide

This document provides comprehensive information for deploying the Medical PDF to Anki Converter in various environments, from local development to production servers.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Cloudflare Tunnel](#cloudflare-tunnel)
- [Production Server Deployment](#production-server-deployment)
- [Environment Configuration](#environment-configuration)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Backup and Recovery](#backup-and-recovery)
- [Security Considerations](#security-considerations)

---

## Deployment Options

### Summary

| Option | Complexity | Cost | Best For |
|--------|------------|------|----------|
| Local Docker | Low | Free | Personal use, testing |
| Cloudflare Tunnel | Medium | Free tier | Small teams, remote access |
| VPS (DigitalOcean, Linode) | Medium | $5-10/month | Production, custom domain |
| Cloud Run / Lambda | High | Pay-per-use | Scalable, serverless |
| Kubernetes | High | Varies | Enterprise, high availability |

---

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/thies2005/Anki-Ai.git
cd Anki-Ai

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Docker Compose Configuration

The `docker-compose.yml` defines two services:

```yaml
services:
  anki-ai:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ZAI_API_KEY=${ZAI_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  tunnel:
    image: cloudflare/cloudflared:latest
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=${TUNNEL_TOKEN}
    depends_on:
      anki-ai:
        condition: service_healthy
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Production Docker Settings

For production, modify `docker-compose.yml`:

```yaml
services:
  anki-ai:
    # ... existing config ...
    command: [
      "streamlit", "run", "app.py",
      "--server.port=8501",
      "--server.address=0.0.0.0",
      "--server.headless=true",
      "--server.enableCORS=false",
      "--server.enableXsrfProtection=true",
      "--server.cookieSecretFile=/run/secrets/cookie_secret"
    ]
    secrets:
      - cookie_secret
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

secrets:
  cookie_secret:
    file: ./secrets/cookie_secret.txt
```

---

## Cloudflare Tunnel

Cloudflare Tunnel provides secure remote access without opening ports on your server.

### Option 1: Tunnel Token (Simple)

1. **Generate Tunnel Token**

   - Login to [Cloudflare Zero Trust](https://dash.cloudflare.com/sign-up/teams)
   - Navigate to: `Zero Trust > Access > Tunnels`
   - Click "Create a tunnel"
   - Select "Docker" as the platform
   - Copy the tunnel token

2. **Configure `.env`**

   ```env
   TUNNEL_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. **Start Services**

   ```bash
   docker compose up -d
   ```

4. **Access Your App**

   - Check logs for the public URL
   - Or configure a custom subdomain in Cloudflare dashboard

### Option 2: Full Configuration (Advanced)

For more control, use a full Cloudflare tunnel configuration.

#### 1. Create Tunnel

```bash
# Install cloudflared
# Linux (amd64)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create anki-ai

# Note the tunnel ID from output
```

#### 2. Configure Tunnel

Create `cloudflared/config.yml`:

```yaml
tunnel: YOUR_TUNNEL_UUID
credentials-file: /home/cloudflared/.cloudflared/YOUR_TUNNEL_UUID.json

ingress:
  # Your application
  - hostname: anki.yourdomain.com
    service: http://anki-ai:8501
    # Optional: require authentication
    originRequest:
      noTLSVerify: true

  # Health check endpoint
  - service: http_status:404
```

#### 3. Copy Credentials

```bash
mkdir -p cloudflared

# Copy certificate
cp ~/.cloudflared/*.cert cloudflared/

# Copy tunnel credentials
cp ~/.cloudflared/YOUR_TUNNEL_UUID.json cloudflared/

# Set permissions
chmod 600 cloudflared/*
```

#### 4. Update docker-compose.yml

```yaml
services:
  tunnel:
    image: cloudflare/cloudflared:latest
    command: tunnel --config /home/cloudflared/.cloudflared/config.yml run
    volumes:
      - ./cloudflared:/home/cloudflared/.cloudflared:ro
    depends_on:
      anki-ai:
        condition: service_healthy
```

#### 5. Add DNS Record

```bash
cloudflared tunnel route dns anki-ai anki.yourdomain.com
```

---

## Production Server Deployment

### Server Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 1 GB | 2+ GB |
| Storage | 10 GB | 20+ GB |
| OS | Ubuntu 22.04+ | Ubuntu 22.04 LTS |

### DigitalOcean Deployment

#### 1. Create Droplet

```bash
# Using doctl CLI
doctl compute droplet create anki-ai \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --ssh-keys YOUR_SSH_KEY_FINGERPRINT
```

#### 2. SSH into Server

```bash
ssh root@your.droplet.ip
```

#### 3. Install Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Enable and start Docker
systemctl enable docker
systemctl start docker
```

#### 4. Deploy Application

```bash
# Clone repository
git clone https://github.com/thies2005/Anki-Ai.git
cd Anki-Ai

# Configure environment
cp .env.example .env
nano .env  # Edit your configuration

# Start services
docker compose up -d
```

#### 5. Configure Firewall

```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS (if not using tunnel)
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable
```

#### 6. Set Up SSL with Nginx (Optional)

```bash
# Install Nginx
apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx
cat > /etc/nginx/sites-available/anki-ai << 'EOF'
server {
    listen 80;
    server_name anki.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/anki-ai /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d anki.yourdomain.com
```

---

## Environment Configuration

### Required Environment Variables

Create a `.env` file from `.env.example`:

```env
# ========== API Keys ==========
# At least one provider is required

# Google AI (Gemini)
GOOGLE_API_KEY=your_gemini_key_here

# Z.AI
ZAI_API_KEY=your_zai_key_here

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional: Fallback keys
FALLBACK_KEY_1=your_backup_key_here

# ========== SMTP Configuration ==========
# For password reset and welcome emails

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# ========== AnkiConnect ==========
# Default URL for Anki Desktop addon
ANKI_CONNECT_URL=http://localhost:8765

# ========== Cloudflare Tunnel ==========
# Optional: For remote access
TUNNEL_TOKEN=your_tunnel_token_here

# ========== Security ==========
# Secret for session encryption (generate your own)
SESSION_SECRET=generate_a_long_random_string_here

# ========== Application Settings ==========
# Chunk size for PDF processing (characters)
DEFAULT_CHUNK_SIZE=20000

# Maximum upload size (MB)
MAX_UPLOAD_SIZE=100

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### Generating Secrets

```bash
# Generate session secret
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate cookie secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Monitoring and Maintenance

### Health Checks

The application includes built-in health checks:

```bash
# Check application health
curl http://localhost:8501/_stcore/health

# Expected response
# {"status": "healthy"}
```

### Viewing Logs

```bash
# Streamlit logs
docker compose logs -f anki-ai

# Cloudflare tunnel logs
docker compose logs -f tunnel

# All logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100 anki-ai
```

### Log Rotation

Configure log rotation in `/etc/logrotate.d/anki-ai`:

```
/home/ubuntu/Anki-Ai/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        docker compose restart anki-ai
    endscript
}
```

### Monitoring with Prometheus (Optional)

Add to `docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-storage:/var/lib/grafana
    ports:
      - "3001:3000"
```

---

## Backup and Recovery

### Backup Strategy

#### 1. Automated Backup Script

Create `backup.sh`:

```bash
#!/bin/bash
# Backup script for Anki-Ai

BACKUP_DIR="/home/ubuntu/backups/anki-ai"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/ubuntu/Anki-Ai"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup user data
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" -C "$APP_DIR" data/

# Backup database (vector store)
cp "$APP_DIR/data/vector_store.db" "$BACKUP_DIR/vector_store_$DATE.db"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete

echo "Backup completed: $DATE"
```

#### 2. Schedule with Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/ubuntu/Anki-Ai/backup.sh >> /var/log/anki-backup.log 2>&1
```

#### 3. Restore from Backup

```bash
# Stop services
docker compose down

# Restore data
tar -xzf /home/ubuntu/backups/anki-ai/data_20250101_020000.tar.gz -C /home/ubuntu/Anki-Ai

# Restart services
docker compose up -d
```

### Cloud Backup (Optional)

#### AWS S3 Backup

```bash
# Install AWS CLI
apt install awscli -y

# Configure
aws configure

# Backup script
#!/bin/bash
aws s3 sync /home/ubuntu/Anki-Ai/data s3://your-bucket/anki-ai-backup/$(date +%Y%m%d)/
```

#### Google Cloud Storage Backup

```bash
# Install gcloud CLI
apt install google-cloud-cli -y

# Authenticate
gcloud auth login

# Backup script
#!/bin/bash
gsutil -m rsync -r /home/ubuntu/Anki-Ai/data gs://your-bucket/anki-ai-backup/$(date +%Y%m%d)/
```

---

## Security Considerations

### Hardening Guide

#### 1. System Security

```bash
# Update system regularly
apt update && apt upgrade -y

# Configure automatic security updates
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# Use SSH keys only
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd
```

#### 2. Application Security

```bash
# Set proper file permissions
chmod 600 /home/ubuntu/Anki-Ai/.env
chmod 700 /home/ubuntu/Anki-Ai/data
chmod 644 /home/ubuntu/Anki-Ai/data/*.json
chmod 600 /home/ubuntu/Anki-Ai/data/users.json

# Run as non-root user
```

Add to `Dockerfile`:

```dockerfile
# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
```

#### 3. Network Security

```bash
# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow from YOUR_IP_ADDRESS to any port 22
ufw enable

# Install fail2ban
apt install fail2ban -y
systemctl enable fail2ban
```

#### 4. Docker Security

```bash
# Run containers in read-only mode (where possible)
# Use Docker secrets for sensitive data
# Enable content trust
export DOCKER_CONTENT_TRUST=1

# Scan images for vulnerabilities
docker scout cves anki-ai
```

---

## Troubleshooting Deployment Issues

### Issue: Container Won't Start

```bash
# Check logs
docker compose logs anki-ai

# Check resource usage
docker stats

# Rebuild without cache
docker compose build --no-cache
docker compose up -d
```

### Issue: Cloudflare Tunnel Connection Failed

```bash
# Verify tunnel token
echo $TUNNEL_TOKEN

# Check tunnel logs
docker compose logs tunnel

# Restart tunnel
docker compose restart tunnel
```

### Issue: High Memory Usage

```bash
# Add memory limits to docker-compose.yml
services:
  anki-ai:
    deploy:
      resources:
        limits:
          memory: 2G

# Or increase server RAM
```

### Issue: Database Corruption

```bash
# Stop services
docker compose down

# Backup and recreate database
mv data/vector_store.db data/vector_store.db.backup

# Restart (will create new database)
docker compose up -d
```

---

## Performance Tuning

### Streamlit Configuration

Add to `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false
showErrorDetails = false

[runner]
magicEnabled = false
```

### Worker Processes

For higher traffic, run multiple instances:

```yaml
services:
  anki-ai:
    deploy:
      replicas: 3
```

And add a load balancer (nginx):

```nginx
upstream anki_ai {
    server anki-ai-1:8501;
    server anki-ai-2:8501;
    server anki-ai-3:8501;
}

server {
    listen 80;
    location / {
        proxy_pass http://anki_ai;
    }
}
```

---

*Last updated: 2025*

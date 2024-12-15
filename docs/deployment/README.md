# Deployment Guide

## Overview

This guide covers deploying the Book Tracker application to a production environment, including server setup, configuration, monitoring, and maintenance.

## Server Requirements

### Hardware Requirements
- CPU: 2+ cores
- RAM: 4GB minimum
- Storage: 20GB minimum
- Network: 100Mbps minimum

### Software Requirements
- Python 3.8+
- SQLite 3.35+
- Nginx 1.18+
- Supervisor or systemd
- SSL certificate
- Git

## Production Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx supervisor sqlite3

# Create application user
sudo useradd -m -s /bin/bash booktracker
sudo usermod -aG www-data booktracker
```

### 2. Application Setup

```bash
# Switch to application user
sudo su - booktracker

# Clone repository
git clone https://github.com/joereg4/book_tracker.git
cd book_tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

### 3. Environment Configuration

Create `.env` file:
```plaintext
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_SECRET_KEY=<generated-secret-key>
GOOGLE_BOOKS_API_KEY=<your-api-key>
DATABASE_URL=sqlite:///instance/books.db

# Email settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=<email>
MAIL_PASSWORD=<password>
MAIL_DEFAULT_SENDER=<sender-email>

# Security settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=2592000  # 30 days in seconds
```

### 4. Database Setup

```bash
# Create instance directory
mkdir -p instance

# Initialize database
flask db upgrade

# Set up FTS tables
python rebuild_fts_search.py

# Set permissions
chmod 600 instance/books.db
```

## Web Server Configuration

### 1. Gunicorn Setup

Create `gunicorn_config.py`:
```python
bind = 'unix:/home/booktracker/book_tracker/book_tracker.sock'
workers = 3
timeout = 120
accesslog = '/home/booktracker/book_tracker/logs/access.log'
errorlog = '/home/booktracker/book_tracker/logs/error.log'
capture_output = True
```

### 2. Supervisor Configuration

Create `/etc/supervisor/conf.d/book_tracker.conf`:
```ini
[program:book_tracker]
directory=/home/booktracker/book_tracker
command=/home/booktracker/book_tracker/venv/bin/gunicorn -c gunicorn_config.py wsgi:app
user=booktracker
autostart=true
autorestart=true
stderr_logfile=/home/booktracker/book_tracker/logs/supervisor.err.log
stdout_logfile=/home/booktracker/book_tracker/logs/supervisor.out.log
environment=
    FLASK_ENV="production",
    FLASK_DEBUG="0"
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/book_tracker`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    access_log /var/log/nginx/book_tracker_access.log;
    error_log /var/log/nginx/book_tracker_error.log;

    location / {
        proxy_pass http://unix:/home/booktracker/book_tracker/book_tracker.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/booktracker/book_tracker/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/book_tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate

### Let's Encrypt Setup

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring

### 1. Application Monitoring

Install monitoring tools:
```bash
pip install prometheus_client
pip install flask_prometheus_metrics
```

### 2. System Monitoring

```bash
# Install monitoring tools
sudo apt install -y prometheus node-exporter grafana

# Configure Prometheus
sudo nano /etc/prometheus/prometheus.yml

# Add job for Book Tracker metrics
scrape_configs:
  - job_name: 'book_tracker'
    static_configs:
      - targets: ['localhost:8000']
```

### 3. Log Monitoring

```bash
# Install log monitoring
sudo apt install -y logrotate

# Configure log rotation
sudo nano /etc/logrotate.d/book_tracker
```

## Backup Strategy

### 1. Database Backup

Create backup script `/home/booktracker/book_tracker/scripts/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/home/booktracker/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sqlite3 /home/booktracker/book_tracker/instance/books.db ".backup '$BACKUP_DIR/books_$TIMESTAMP.db'"
find $BACKUP_DIR -name "books_*.db" -mtime +7 -delete
```

### 2. Automated Backups

Add to crontab:
```bash
0 2 * * * /home/booktracker/book_tracker/scripts/backup.sh
```

## Maintenance

### 1. Updates

Create update script `scripts/update.sh`:
```bash
#!/bin/bash
cd /home/booktracker/book_tracker
source venv/bin/activate
git pull
pip install -r requirements.txt
flask db upgrade
sudo supervisorctl restart book_tracker
```

### 2. Health Checks

Create health check endpoint:
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

## Deployment Checklist

### Pre-deployment
- [ ] Run all tests
- [ ] Check dependencies
- [ ] Update documentation
- [ ] Backup database

### Configuration
- [ ] Environment variables set
- [ ] Debug mode disabled
- [ ] Secret key configured
- [ ] SSL certificates installed

### Security
- [ ] Firewall configured
- [ ] Security headers enabled
- [ ] File permissions set
- [ ] Backup system tested

### Monitoring
- [ ] Logging configured
- [ ] Monitoring tools setup
- [ ] Alerts configured
- [ ] Backup automation verified

## Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Check logs: `/home/booktracker/book_tracker/logs/`
   - Verify permissions
   - Check configuration
   - Validate environment

2. **Database Issues**
   - Check SQLite version
   - Verify file permissions
   - Run migrations
   - Check backup integrity

3. **Performance Issues**
   - Monitor resource usage
   - Check Gunicorn workers
   - Analyze Nginx logs
   - Review database queries

## Further Reading

- [Flask Deployment](https://flask.palletsprojects.com/en/2.0.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/) 
# Server Configuration Template

This document provides templates for server configuration files. When deploying, create actual configuration files with appropriate values for your environment.

## Systemd Service Template

File: `/etc/systemd/system/book_tracker.service`

```ini
[Unit]
Description=Book Tracker Web Application
After=network.target postgresql.service

[Service]
User=<app_user>
Group=<app_group>
WorkingDirectory=<app_path>
Environment="PATH=<venv_path>/bin"
EnvironmentFile=<app_path>/.env
ExecStart=<venv_path>/bin/gunicorn \
    --workers <num_workers> \
    --bind unix:book_tracker.sock \
    --access-logfile <log_path>/access.log \
    --error-logfile <log_path>/error.log \
    wsgi:app

[Install]
WantedBy=multi-user.target
```

Replace placeholders:
- `<app_user>`: Application system user
- `<app_group>`: Application system group
- `<app_path>`: Full path to application directory
- `<venv_path>`: Full path to virtual environment
- `<num_workers>`: Number of Gunicorn workers (typically 2-4)
- `<log_path>`: Path to log directory

## Log Rotation Template

File: `/etc/logrotate.d/book_tracker`

```conf
<log_path>/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 <app_user> <app_group>
    sharedscripts
    postrotate
        systemctl reload book_tracker.service
    endscript
}
```

## Nginx Site Template

File: `/etc/nginx/sites-available/book_tracker`

```nginx
server {
    listen 80;
    server_name <your_domain>;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name <your_domain>;

    # SSL configuration
    ssl_certificate <path_to_fullchain>;
    ssl_certificate_key <path_to_privkey>;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Recommended cipher suite
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

    # Application proxy
    location / {
        proxy_pass http://unix:<app_path>/book_tracker.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static {
        alias <app_path>/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';";
}
```

## Security Recommendations

1. File Permissions:
   - Configuration files: `644`
   - SSL certificates: `600`
   - Application files: `750`
   - Log directory: `750`

2. Directory Structure:
   ```
   /home/<app_user>/
   └── book_tracker/
       ├── venv/
       ├── static/
       ├── logs/
       └── .env
   ```

3. SSL Certificates:
   - Use Let's Encrypt for free SSL
   - Set up automatic renewal
   - Keep backups of certificates

4. Monitoring:
   - Set up log monitoring
   - Configure error notifications
   - Monitor system resources

## Deployment Checklist

1. [ ] Create application user and group
2. [ ] Set up directory structure
3. [ ] Configure virtual environment
4. [ ] Set up SSL certificates
5. [ ] Create and configure service file
6. [ ] Set up log rotation
7. [ ] Configure Nginx
8. [ ] Set correct file permissions
9. [ ] Test configuration
10. [ ] Enable and start services 
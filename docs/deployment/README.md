# Deployment Guide

This guide covers the deployment process for the Book Tracker application.

## Documentation Structure

- `server_config.md`: Sensitive server configurations (not in repo)
- `postgres_migration.md`: Database migration guide
- `backup_restore.md`: Backup and restore procedures

## Pre-Deployment Checklist

1. Server Requirements:
   - Ubuntu 22.04 LTS or newer
   - Python 3.11+
   - PostgreSQL 14+
   - Nginx
   - Let's Encrypt SSL certificate

2. Domain and SSL:
   - Registered domain name
   - DNS configured
   - SSL certificate ready

3. Environment:
   - All environment variables set
   - PostgreSQL credentials secured
   - Application secrets generated

## Deployment Steps

1. **Initial Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install required packages
   sudo apt install python3-pip postgresql nginx certbot python3-certbot-nginx
   ```

2. **Application Setup**
   ```bash
   # Create application user
   sudo useradd -m -s /bin/bash books_app
   
   # Clone repository
   git clone https://github.com/yourusername/book_tracker.git
   
   # Set up virtual environment
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   - Follow `postgres_migration.md` for database setup
   - Run initial migrations
   - Verify database connection

4. **Server Configuration**
   - Follow `server_config.md` for sensitive configurations:
     - Systemd service setup
     - Log rotation
     - Nginx configuration
     - SSL setup

5. **Security Setup**
   - Configure firewall
   - Set up fail2ban
   - Secure file permissions
   - Enable automatic security updates

## Post-Deployment

1. **Verification**:
   - Test all application features
   - Verify SSL configuration
   - Check log rotation
   - Test backup system

2. **Monitoring**:
   - Set up application monitoring
   - Configure error notifications
   - Enable performance monitoring

3. **Maintenance**:
   - Schedule regular backups
   - Plan security updates
   - Monitor disk space
   - Check log files

## Troubleshooting

Common issues and solutions:

1. **Application Errors**:
   ```bash
   # Check application logs
   sudo journalctl -u book_tracker.service
   
   # Check nginx logs
   sudo tail -f /var/log/nginx/error.log
   ```

2. **Database Issues**:
   ```bash
   # Check PostgreSQL logs
   sudo tail -f /var/log/postgresql/postgresql-14-main.log
   ```

3. **Permission Problems**:
   ```bash
   # Fix common permission issues
   sudo chown -R books_app:books_app /home/books_app/book_tracker
   sudo chmod -R 750 /home/books_app/book_tracker
   ```

## Backup and Recovery

See `backup_restore.md` for detailed procedures on:
- Daily automated backups
- Manual backup creation
- Backup verification
- Recovery procedures

## Updates and Maintenance

1. **Code Updates**:
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run migrations
   flask db upgrade
   
   # Restart service
   sudo systemctl restart book_tracker
   ```

2. **System Updates**:
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Restart if needed
   sudo systemctl restart book_tracker
   ```

## Security Considerations

1. **Access Control**:
   - Minimal user privileges
   - Secure SSH configuration
   - Regular security audits

2. **Data Protection**:
   - Regular backups
   - Encrypted connections
   - Secure data handling

3. **Monitoring**:
   - Failed login attempts
   - System resource usage
   - Application errors 

## Email Configuration

1. **SMTP Setup**:
   ```bash
   # Production email settings in .env
   FLASK_ENV=production
   MAIL_SERVER=smtp.your-provider.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email
   MAIL_PASSWORD=your_secure_password
   MAIL_DEFAULT_SENDER=noreply@your-domain.com
   ```

2. **Email Testing**:
   ```bash
   # Test email configuration
   flask email-cli test admin@your-domain.com
   
   # Check logs for errors
   sudo journalctl -u book_tracker.service | grep "email"
   ```

3. **Security Considerations**:
   - Use environment variables for credentials
   - Enable TLS/SSL for email
   - Monitor failed email attempts
   - Regularly rotate email credentials
   - Set up email signing (DKIM/SPF)

4. **Monitoring**:
   - Set up email delivery monitoring
   - Configure bounce notifications
   - Track email sending rates
   - Monitor spam reports 
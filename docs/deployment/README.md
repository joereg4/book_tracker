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
   - Postfix mail server

2. Domain and SSL:
   - Registered domain name
   - DNS configured (including MX records)
   - SSL certificate ready
   - SPF and DKIM records set up for email

3. Environment:
   - All environment variables set
   - PostgreSQL credentials secured
   - Application secrets generated
   - Google Books API key configured
   - Redis configured for rate limiting
   - Postfix configured for transactional emails

## Deployment Steps

1. **Initial Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install required packages
   sudo apt install python3-pip postgresql nginx certbot python3-certbot-nginx redis-server postfix opendkim opendkim-tools
   ```

2. **Email Server Setup**

   a. Initial Postfix Configuration:
   ```bash
   # During Postfix installation, select 'Internet Site'
   # System mail name: your-domain.com
   
   # Edit main Postfix configuration
   sudo nano /etc/postfix/main.cf
   ```
   
   Add/modify these settings:
   ```
   # Basic Settings
   myhostname = mail.your-domain.com
   mydomain = your-domain.com
   myorigin = $mydomain
   inet_interfaces = all
   mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain
   
   # TLS Settings
   smtpd_tls_cert_file = /etc/letsencrypt/live/your-domain.com/fullchain.pem
   smtpd_tls_key_file = /etc/letsencrypt/live/your-domain.com/privkey.pem
   smtpd_use_tls = yes
   smtpd_tls_auth_only = yes
   
   # Security Settings
   smtpd_sasl_type = dovecot
   smtpd_sasl_auth_enable = yes
   smtpd_recipient_restrictions = 
       permit_sasl_authenticated,
       permit_mynetworks,
       reject_unauth_destination
   ```

   b. Configure OpenDKIM:
   ```bash
   # Generate DKIM keys
   sudo mkdir -p /etc/opendkim/keys/your-domain.com
   cd /etc/opendkim/keys/your-domain.com
   sudo opendkim-genkey -s mail -d your-domain.com
   
   # Set permissions
   sudo chown -R opendkim:opendkim /etc/opendkim/keys
   
   # Configure OpenDKIM
   sudo nano /etc/opendkim.conf
   ```
   
   Add these settings:
   ```
   Domain                  your-domain.com
   KeyFile                 /etc/opendkim/keys/your-domain.com/mail.private
   Selector               mail
   ```

   c. Set up DNS Records:
   ```
   # Add these DNS records to your domain
   
   # MX Record
   your-domain.com.    IN    MX    10    mail.your-domain.com.
   
   # SPF Record
   your-domain.com.    IN    TXT    "v=spf1 mx a ip4:YOUR_SERVER_IP -all"
   
   # DKIM Record (copy from mail.txt generated earlier)
   mail._domainkey.your-domain.com.    IN    TXT    "v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY"
   
   # DMARC Record
   _dmarc.your-domain.com.    IN    TXT    "v=DMARC1; p=quarantine; rua=mailto:postmaster@your-domain.com"
   ```

   d. Test Email Configuration:
   ```bash
   # Test Postfix configuration
   sudo postfix check
   
   # Test DKIM signing
   sudo opendkim-testkey -d your-domain.com -s mail -vvv
   
   # Send test email
   echo "Test email" | mail -s "Test Subject" test@your-domain.com
   
   # Check logs
   sudo tail -f /var/log/mail.log
   ```

   e. Configure Application Email Settings:
   ```
   # Production email settings in .env
   MAIL_SERVER=localhost
   MAIL_PORT=25
   MAIL_USE_TLS=False
   MAIL_USERNAME=noreply
   MAIL_PASSWORD=
   MAIL_DEFAULT_SENDER=noreply@your-domain.com
   ```

3. **Application Setup**
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

4. **Database Setup**
   - Follow `postgres_migration.md` for database setup
   - Run initial migrations
   - Verify database connection

5. **Server Configuration**
   - Follow `server_config.md` for sensitive configurations:
     - Systemd service setup
     - Log rotation
     - Nginx configuration
     - SSL setup

6. **Security Setup**
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

The application uses Gmail's OAuth2 for sending emails, with the following setup:

1. Gmail Account Setup:
   - Primary email: `noreply.readkeeper@gmail.com`
   - Used with OAuth2 for secure email sending

2. Domain Email Forwarding (Cloudflare):
   - Public-facing email: `noreply@readkeeper.com`
   - Forwards to: `noreply.readkeeper@gmail.com`
   - Configured through Cloudflare Email Routing

3. OAuth2 Configuration:
   ```bash
   # Production OAuth2 settings in .env
   FLASK_ENV=production
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USE_OAUTH2=True
   MAIL_USERNAME=noreply.readkeeper@gmail.com
   MAIL_DEFAULT_SENDER=noreply@readkeeper.com
   MAIL_OAUTH_CLIENT_ID=your_oauth_client_id
   MAIL_OAUTH_CLIENT_SECRET=your_oauth_client_secret
   MAIL_OAUTH_REFRESH_TOKEN=your_oauth_refresh_token
   ```

4. Email Testing:
   ```bash
   # Test email configuration
   flask email-cli test admin@your-domain.com
   
   # Check logs for errors
   sudo journalctl -u book_tracker.service | grep "email"
   ```

5. Security Considerations:
   - Use environment variables for credentials
   - Enable TLS/SSL for email
   - Monitor failed email attempts
   - Regularly rotate OAuth2 credentials
   - Set up email signing (DKIM/SPF)

6. Monitoring:
   - Set up email delivery monitoring
   - Configure bounce notifications
   - Track email sending rates
   - Monitor spam reports 

## Email Monitoring and Maintenance

1. **Log Monitoring**:
   ```bash
   # Monitor mail logs
   sudo tail -f /var/log/mail.log
   
   # Check for blocked emails
   sudo postqueue -p
   ```

2. **Email Queue Management**:
   ```bash
   # View mail queue
   mailq
   
   # Flush mail queue
   sudo postfix flush
   
   # Delete all queued mail
   sudo postsuper -d ALL
   ```

3. **Regular Maintenance**:
   - Monitor disk space for mail queue
   - Check mail logs for errors
   - Verify DKIM/SPF records
   - Test email delivery regularly
   - Monitor spam scores

4. **Troubleshooting**:
   ```bash
   # Test Postfix configuration
   sudo postfix check
   
   # Test mail delivery
   echo "Test" | mail -s "Test" test@your-domain.com
   
   # Check mail logs
   sudo grep "error" /var/log/mail.log
   
   # Test DKIM signing
   sudo opendkim-testkey -d your-domain.com -s mail
   ```

5. **Security Best Practices**:
   - Regularly update Postfix and OpenDKIM
   - Monitor for suspicious activity
   - Keep TLS certificates up to date
   - Review mail logs for security issues
   - Maintain SPF and DKIM records 
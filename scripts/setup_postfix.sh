#!/bin/bash

# Exit on error
set -e

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Get domain name and IP from environment or prompt
DOMAIN=${DOMAIN:-$(read -p "Enter your domain name (e.g., readkeeper.com): " domain && echo $domain)}
SERVER_IP=${SERVER_IP:-$(read -p "Enter your server's public IP address: " ip && echo $ip)}

echo "Installing Postfix and OpenDKIM..."

# Update package lists and install required packages
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common
add-apt-repository -y universe
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y postfix opendkim opendkim-tools

# Backup original configs
echo "Backing up original configurations..."
cp /etc/postfix/main.cf /etc/postfix/main.cf.bak || true
cp /etc/opendkim.conf /etc/opendkim.conf.bak || true

# Configure Postfix
echo "Configuring Postfix..."
cat > /etc/postfix/main.cf << EOF
# Basic Settings
myhostname = mail.$DOMAIN
mydomain = $DOMAIN
myorigin = \$mydomain
inet_interfaces = all
mydestination = \$myhostname, localhost.\$mydomain, localhost, \$mydomain

# TLS Settings
smtpd_tls_cert_file = /etc/letsencrypt/live/$DOMAIN/fullchain.pem
smtpd_tls_key_file = /etc/letsencrypt/live/$DOMAIN/privkey.pem
smtpd_use_tls = yes
smtpd_tls_auth_only = yes

# Security Settings
smtpd_sasl_type = dovecot
smtpd_sasl_auth_enable = yes
smtpd_recipient_restrictions = 
    permit_sasl_authenticated,
    permit_mynetworks,
    reject_unauth_destination

# DKIM Settings
milter_protocol = 2
milter_default_action = accept
smtpd_milters = inet:localhost:8891
non_smtpd_milters = inet:localhost:8891
EOF

# Configure OpenDKIM
echo "Configuring OpenDKIM..."
mkdir -p /etc/opendkim/keys/$DOMAIN
cd /etc/opendkim/keys/$DOMAIN
opendkim-genkey -s mail -d $DOMAIN

# Set permissions
chown -R opendkim:opendkim /etc/opendkim/keys

# Configure OpenDKIM main config
cat > /etc/opendkim.conf << EOF
Domain                  $DOMAIN
KeyFile                 /etc/opendkim/keys/$DOMAIN/mail.private
Selector               mail
Socket                 inet:8891@localhost
EOF

# Create OpenDKIM socket directory
mkdir -p /var/run/opendkim
chown opendkim:opendkim /var/run/opendkim

# Display DNS records to add
echo "================================================================"
echo "Add these DNS records to your domain configuration:"
echo "================================================================"
echo
echo "MX Record:"
echo "$DOMAIN.    IN    MX    10    mail.$DOMAIN."
echo
echo "SPF Record:"
echo "$DOMAIN.    IN    TXT    \"v=spf1 mx a ip4:$SERVER_IP -all\""
echo
echo "DKIM Record (add this to mail._domainkey.$DOMAIN):"
cat /etc/opendkim/keys/$DOMAIN/mail.txt
echo
echo "DMARC Record:"
echo "_dmarc.$DOMAIN.    IN    TXT    \"v=DMARC1; p=quarantine; rua=mailto:postmaster@$DOMAIN\""
echo
echo "================================================================"

# Restart services if systemd is available
if command -v systemctl >/dev/null 2>&1; then
    echo "Restarting services using systemctl..."
    systemctl restart opendkim || true
    systemctl restart postfix || true
else
    echo "Restarting services using service command..."
    service opendkim restart || true
    service postfix restart || true
fi

# Create test script
cat > /usr/local/bin/test_email << EOF
#!/bin/bash
if [ -z "\$1" ]; then
    echo "Usage: test_email recipient@example.com"
    exit 1
fi
echo "Test email from $DOMAIN" | mail -s "Test Email" \$1
echo "Test email sent to \$1. Check /var/log/mail.log for delivery status."
EOF

chmod +x /usr/local/bin/test_email

echo "================================================================"
echo "Setup complete! Here's what to do next:"
echo "1. Add the DNS records shown above to your domain configuration"
echo "2. Wait for DNS propagation (usually 5-30 minutes)"
echo "3. Run a test email: test_email your@email.com"
echo "4. Check mail logs: tail -f /var/log/mail.log"
echo "5. Update your application's .env file with these settings:"
echo
cat << EOF
MAIL_SERVER=localhost
MAIL_PORT=25
MAIL_USE_TLS=False
MAIL_USERNAME=noreply
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@$DOMAIN
EOF
echo "================================================================" 
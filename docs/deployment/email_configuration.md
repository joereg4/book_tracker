# Email Configuration Guide

## Prerequisites
- Postfix installed and basic setup completed via `setup_postfix.sh`
- Domain name configured with proper DNS records (MX, SPF, DKIM, DMARC)
- OpenDKIM installed

## OpenDKIM Configuration

After running the setup script, additional configuration for OpenDKIM is required:

1. Update the OpenDKIM configuration file:
```bash
sudo nano /etc/opendkim.conf
```

Add the following content:
```
# Basics
Syslog                  yes
UMask                   002
Mode                    sv
PidFile                 /run/opendkim/opendkim.pid
Socket                  inet:8891@localhost

# Signing
Canonicalization        relaxed/simple
Domain                  example.com
KeyTable                /etc/opendkim/key.table
SigningTable           refile:/etc/opendkim/signing.table
ExternalIgnoreList     refile:/etc/opendkim/trusted.hosts
InternalHosts          refile:/etc/opendkim/trusted.hosts
```

2. Create and configure the required files:
```bash
# Create directories and files
sudo mkdir -p /etc/opendkim
sudo touch /etc/opendkim/key.table
sudo touch /etc/opendkim/signing.table
sudo touch /etc/opendkim/trusted.hosts

# Configure key table
echo "mail._domainkey.example.com example.com:mail:/etc/opendkim/keys/example.com/mail.private" | sudo tee /etc/opendkim/key.table

# Configure signing table
echo "*@example.com mail._domainkey.example.com" | sudo tee /etc/opendkim/signing.table

# Configure trusted hosts
echo "127.0.0.1
localhost
example.com" | sudo tee /etc/opendkim/trusted.hosts
```

3. Restart OpenDKIM:
```bash
sudo systemctl restart opendkim
sudo systemctl status opendkim
```

## Verification Steps

1. Check OpenDKIM status:
```bash
sudo systemctl status opendkim
```

2. Test email sending:
```bash
echo "Test email" | mail -s "Test Subject" recipient@example.com
```

3. Monitor mail logs:
```bash
sudo tail -f /var/log/mail.log
```

## Troubleshooting

Common issues and solutions:

1. OpenDKIM fails to start:
   - Check configuration syntax
   - Verify file permissions
   - Check log files: `sudo journalctl -u opendkim`

2. Emails not being signed:
   - Verify Socket configuration matches between Postfix and OpenDKIM
   - Check key permissions
   - Verify key.table and signing.table configurations

3. Emails not being delivered:
   - Check if port 25 is blocked by your provider
   - Verify DNS records are properly propagated
   - Check mail logs for specific error messages

Note: Replace `example.com` with your actual domain name in all configurations. 
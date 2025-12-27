# SSL Renew instructions

1. SSH your EC2
2. Install nginx
```sudo apt update && sudo apt install nginx -y```
3. Create a site file
```sudo nano /etc/apache2/sites-available/<subdomain name>```
4. Add the config with server_name (refer site_config.txt)
5. Enable the site
```sudo ln -s /etc/nginx/sites-available/<subdomain name> /etc/nginx/sites-enabled/```
```sudo systemctl reload nginx```

6. Set up SSL
```sudo apt install certbot python3-certbot-nginx -y  # For Nginx```
7. Generate SSL certificate
```sudo certbot --nginx -d blog.yourdomain.com   # For Nginx```
8. Go to hostinger/domain provider, add an A record pointing to the server IP (Elastic ip)

9. Navigate to the subdomain to validate

## Troubleshooting

1. Permissions check
```sudo chown -R www-data:www-data /var/www/subdomain```
```sudo chmod -R 755 /var/www/subdomain```

2.Test Nginx Configuration:

```bash
sudo nginx -t
```
```bash
sudo systemctl reload nginx
```
```bash
sudo certbot renew --dry-run
```

3. Check DNS propogation
```bash
dig A riteup.mlguide.in +short
```

** Make sure port 443 and 880 are allowed for 0.0.0.0/0 in inbound rules in EC2

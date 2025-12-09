# Djarvis Deployment Guide

## 💻 Local Development

### Prerequisites
- Docker 24.0+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/elementary1997/Djarvis.git
cd Djarvis

# 2. Run setup script
chmod +x scripts/*.sh
./scripts/setup.sh

# 3. Start application
./scripts/start.sh

# 4. Create superuser
docker-compose exec web python manage.py createsuperuser

# 5. Load demo data
docker-compose exec web python manage.py loaddata fixtures/demo_data.json
```

Access the application at:
- **Frontend**: http://localhost
- **Admin**: http://localhost/admin
- **API Docs**: http://localhost/api/docs/

### Development Commands

```bash
# View logs
docker-compose logs -f

# Access Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test

# Stop application
./scripts/stop.sh

# Reset everything (WARNING: deletes all data)
./scripts/reset.sh
```

## 🌐 Production Deployment

### Environment Variables

Update `backend/.env` for production:

```env
DJANGO_SECRET_KEY=<strong-random-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_URL=postgresql://user:pass@db:5432/djarvis
REDIS_URL=redis://redis:6379/0

CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Sentry (optional)
SENTRY_DSN=your-sentry-dsn
```

### SSL/HTTPS Setup

1. **Get SSL Certificates** (Let's Encrypt recommended):

```bash
sudo apt-get install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

2. **Update Nginx Configuration**:

Add to `nginx/conf.d/default.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... rest of configuration
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

3. **Update docker-compose.yml**:

```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Database Backups

```bash
# Backup
docker-compose exec db pg_dump -U djarvis_user djarvis > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20231209.sql | docker-compose exec -T db psql -U djarvis_user djarvis
```

### Monitoring

```bash
# Container stats
docker stats

# Application logs
docker-compose logs -f web

# Celery worker logs
docker-compose logs -f celery_worker

# Nginx logs
docker-compose logs -f nginx
```

## ☁️ Cloud Deployment

### AWS EC2

1. Launch EC2 instance (Ubuntu 22.04, t3.medium minimum)
2. Install Docker and Docker Compose
3. Clone repository
4. Configure security groups (ports 80, 443, 22)
5. Run deployment commands

### DigitalOcean

1. Create Droplet (Docker, 4GB RAM minimum)
2. SSH into droplet
3. Clone and setup application
4. Configure firewall
5. Setup domain and SSL

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml djarvis

# Scale services
docker service scale djarvis_web=3
```

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Use strong database passwords
- [ ] Enable SSL/HTTPS
- [ ] Setup firewall rules
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated
- [ ] Setup Sentry for error tracking

## 🐞 Troubleshooting

### Containers won't start
```bash
docker-compose logs
docker system prune -a  # Clean up
```

### Database connection errors
```bash
docker-compose restart db
docker-compose exec web python manage.py migrate
```

### Sandbox execution fails
```bash
# Check Docker socket permissions
ls -l /var/run/docker.sock
sudo chmod 666 /var/run/docker.sock
```

### Frontend not loading
```bash
docker-compose exec frontend npm run build
docker-compose restart nginx
```

## 📊 Performance Optimization

### Database
- Enable connection pooling
- Add indexes for frequently queried fields
- Use database query optimization

### Caching
- Redis caching is pre-configured
- Consider CDN for static files

### Scaling
- Horizontal scaling: Add more web workers
- Vertical scaling: Increase resource limits
- Use load balancer for multiple instances

## 📞 Support

For issues:
- GitHub Issues: https://github.com/elementary1997/Djarvis/issues
- Email: elipashev2023@yandex.ru

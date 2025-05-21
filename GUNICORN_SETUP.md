# Running LearnMore with Gunicorn

This document describes how to set up and run the LearnMore Django application using Gunicorn.

## Manual Start

To start the server manually:

```bash
# Navigate to the project directory
cd /home/s4512158/www/djangoapps/learnmore

# Make sure the script is executable
chmod +x start_server.sh

# Run the script
./start_server.sh
```

This will start Gunicorn in the foreground. To stop it, press `Ctrl+C`.

## Running as a Systemd Service

For production use, it's recommended to run Gunicorn as a systemd service:

1. Copy the service file to the systemd directory:

```bash
sudo cp /home/s4512158/www/djangoapps/learnmore/learnmore.service /etc/systemd/system/
```

2. Reload systemd:

```bash
sudo systemctl daemon-reload
```

3. Enable the service to start on boot:

```bash
sudo systemctl enable learnmore
```

4. Start the service:

```bash
sudo systemctl start learnmore
```

5. Check the status:

```bash
sudo systemctl status learnmore
```

## Managing the Service

- **Start**: `sudo systemctl start learnmore`
- **Stop**: `sudo systemctl stop learnmore`
- **Restart**: `sudo systemctl restart learnmore`
- **View logs**: `sudo journalctl -u learnmore`

## Nginx Integration

If you're using Nginx as a reverse proxy, add the following to your Nginx site configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /learnmore/static/ {
        alias /home/s4512158/www/djangoapps/learnmore/learnmore/staticfiles/;
    }

    location /learnmore/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Remember to reload Nginx after changes:

```bash
sudo systemctl reload nginx
```

## Troubleshooting

If you encounter any issues:

1. Check the Gunicorn logs:
   ```bash
   tail -f /var/www/djangoapps/learnmore/logs/error.log
   ```

2. Check the system logs:
   ```bash
   sudo journalctl -u learnmore -n 50
   ```

3. Verify permissions:
   ```bash
   # Make sure log directory is writable
   sudo chown -R s4512158:www-data /var/www/djangoapps/learnmore/logs
   sudo chmod 755 /var/www/djangoapps/learnmore/logs
   ```

## Performance Tuning

Adjust the `gunicorn_config.py` file to optimize performance:

- Increase/decrease `workers` based on your server's CPU capacity
- Try different worker classes (gevent, eventlet) for async capabilities
- Adjust timeouts based on your application's needs 
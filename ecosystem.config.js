module.exports = {
  apps : [{
    name: 'pcn',
    cmd: 'main.py',
    autorestart: true,
    watch: true,
    ignore_watch: ["/root/.cache/pypoetry/virtualenvs", "/mnt/Development/Bots/pcn-snek/Logs", "/usr/lib/python3.10"],
    interpreter: '/root/.cache/pypoetry/virtualenvs/pcn-BYjrNVD1-py3.10/bin/python3.10',
    log_date_format: "MMM-DD-YYYY HH:mm A"
  }]
};

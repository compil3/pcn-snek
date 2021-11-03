module.exports = {
  apps : [{
    name: 'pcn',
    cmd: 'bot.py',
    autorestart: true,
    watch: true,
    ignore_watch: ["/root/snek/.venv","/usr/lib", "/root/snek/Logs", "/usr/lib/python3.10"],
    interpreter: '.venv/bin/python3.10'
  }]
};

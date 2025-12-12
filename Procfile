# Procfile para Render, Railway, Heroku
# ======================================

# Web process: Gunicorn con gevent para soporte de WebSockets
web: gunicorn --worker-class gevent -w 1 -b 0.0.0.0:$PORT 'src.main:create_app()'

# Release command: Inicializar base de datos
release: python -m src.main init-db

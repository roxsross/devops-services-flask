#!/usr/bin/env python3
"""
🌐 Flask App mejorada para el Challenge
Una aplicación simple pero con mejores prácticas y experiencia de usuario
"""

import os
import time
import threading
from socket import gethostname, gethostbyname
from datetime import datetime

from flask import Flask, render_template, jsonify

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Información de la aplicación
APP_INFO = {
    'name': 'Flask Challenge App',
    'version': '2.0.0',
    'description': 'Aplicación Flask optimizada para Docker y Kubernetes',
    'author': 'roxsross'
}

# Estado global del consumer
consumer_status = {
    'connected': False,
    'last_seen': None,
    'total_requests': 0,
    'error_count': 0
}


def get_system_info():
    """Obtener información del sistema"""
    try:
        hostname = gethostname()
        ip = gethostbyname(hostname)
        return {
            'hostname': hostname,
            'ip': ip,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'environment': os.environ.get('FLASK_ENV', 'production')
        }
    except Exception as e:
        app.logger.error(f"Error getting system info: {e}")
        return {
            'hostname': 'unknown',
            'ip': 'unknown',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'environment': 'unknown'
        }


def check_consumer_status():
    """Verificar si el consumer está activo basado en las últimas peticiones"""
    if consumer_status['last_seen']:
        time_since_last = (datetime.now() - consumer_status['last_seen']).total_seconds()
        # Si no hemos visto al consumer en más de 10 segundos, marcarlo como desconectado
        if time_since_last > 10:
            consumer_status['connected'] = False
    return consumer_status['connected']


@app.route('/')
def index():
    """Página principal con información del sistema y estado del consumer"""
    context = get_system_info()
    context['consumer_status'] = {
        'connected': check_consumer_status(),
        'last_seen': consumer_status['last_seen'].strftime('%H:%M:%S') if consumer_status['last_seen'] else 'Nunca',
        'total_requests': consumer_status['total_requests'],
        'error_count': consumer_status['error_count']
    }
    return render_template("index.html", context=context)


@app.route('/health')
def health():
    """Endpoint de health check para Kubernetes/Docker"""
    # Este endpoint también registra la actividad del consumer
    consumer_status['total_requests'] += 1
    consumer_status['last_seen'] = datetime.now()
    consumer_status['connected'] = True
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app': APP_INFO,
        'consumer': {
            'connected': consumer_status['connected'],
            'total_requests': consumer_status['total_requests']
        }
    }), 200


@app.route('/api/consumer-heartbeat', methods=['POST', 'GET'])
def consumer_heartbeat():
    """Endpoint para que el consumer registre su actividad"""
    consumer_status['total_requests'] += 1
    consumer_status['last_seen'] = datetime.now()
    consumer_status['connected'] = True
    
    return jsonify({
        'status': 'heartbeat_received',
        'timestamp': datetime.now().isoformat(),
        'consumer_stats': {
            'total_requests': consumer_status['total_requests'],
            'last_seen': consumer_status['last_seen'].isoformat(),
            'connected': consumer_status['connected']
        }
    }), 200


@app.route('/api/info')
def api_info():
    """API endpoint con información del sistema"""
    system_info = get_system_info()
    return jsonify({
        'app': APP_INFO,
        'system': system_info,
        'consumer': {
            'connected': check_consumer_status(),
            'last_seen': consumer_status['last_seen'].isoformat() if consumer_status['last_seen'] else None,
            'total_requests': consumer_status['total_requests'],
            'error_count': consumer_status['error_count']
        }
    }), 200


@app.route('/api/consumer/status')
def consumer_status_api():
    """Endpoint específico para obtener el estado del consumer"""
    return jsonify({
        'connected': check_consumer_status(),
        'last_seen': consumer_status['last_seen'].isoformat() if consumer_status['last_seen'] else None,
        'total_requests': consumer_status['total_requests'],
        'error_count': consumer_status['error_count'],
        'uptime_seconds': (datetime.now() - consumer_status['last_seen']).total_seconds() if consumer_status['last_seen'] else 0
    }), 200


@app.route('/api/consumer/simulate-error')
def simulate_consumer_error():
    """Endpoint para simular un error del consumer (para testing)"""
    consumer_status['connected'] = False
    consumer_status['error_count'] += 1
    consumer_status['last_seen'] = None
    
    return jsonify({
        'message': 'Consumer error simulated',
        'consumer_status': consumer_status
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': [
            '/',
            '/health',
            '/api/info'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'Something went wrong on the server'
    }), 500


if __name__ == '__main__':
    # Configuración del servidor
    host = "0.0.0.0"
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    print("=" * 50)
    print(f"🚀 Starting {APP_INFO['name']} v{APP_INFO['version']}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🐛 Debug mode: {'ON' if debug else 'OFF'}")
    print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    print("=" * 50)
    
    # Iniciar servidor
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

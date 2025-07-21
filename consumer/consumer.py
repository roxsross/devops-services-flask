#!/usr/bin/env python3
"""
🔄 Consumer mejorado para Flask API
Consume la API Flask y muestra el estado de manera clara y amigable
"""

import os
import sys
from time import sleep
from datetime import datetime

import requests
from requests.exceptions import Timeout, ConnectionError, RequestException


def log_message(level, message):
    """Log con timestamp y colores"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = f"[{timestamp}] [{level}]"
    print(f"{prefix} {message}")


def get_config():
    """Obtener configuración desde variables de entorno"""
    config = {
        'api_url': os.getenv('API_URL', 'http://flask-app:8000'),
        'delay': float(os.getenv('CONSUMER_DELAY', '2')),
        'debug': os.getenv('DEBUG_MODE', '0') == '1',
        'simulate_failure': os.getenv('SIMULATE_FAILURE', '0') == '1'
    }
    return config


def test_api_connection(url, debug=False):
    """Probar conexión a la API"""
    try:
        # Hacer llamada al endpoint principal
        response = requests.get(url, timeout=10)
        if response.ok:
            # Ahora hacer llamada al heartbeat para registrar la visita
            heartbeat_url = f"{url}/api/consumer-heartbeat"
            try:
                heartbeat_response = requests.post(heartbeat_url, timeout=5)
                if debug:
                    log_message("DEBUG", f"API Response: {response.status_code}")
                    log_message("DEBUG", f"Heartbeat Response: {heartbeat_response.status_code}")
                    log_message("DEBUG", f"Content length: {len(response.text)} bytes")
            except Exception as heartbeat_error:
                if debug:
                    log_message("DEBUG", f"Heartbeat failed: {heartbeat_error}")
            
            return True, f"✅ API responding correctly (Status: {response.status_code})"
        else:
            return False, f"❌ API error - HTTP {response.status_code}"
    except Timeout:
        return False, f"⏰ Timeout connecting to {url}"
    except ConnectionError:
        return False, f"🔌 Connection failed to {url}"
    except RequestException as e:
        return False, f"❌ Request error: {str(e)}"


def main():
    """Función principal del consumer"""
    config = get_config()
    
    log_message("INFO", "🚀 Starting Flask API Consumer")
    log_message("INFO", f"📡 API URL: {config['api_url']}")
    log_message("INFO", f"⏱️  Check interval: {config['delay']} seconds")
    log_message("INFO", f"🐛 Debug mode: {'ON' if config['debug'] else 'OFF'}")
    
    # Verificar si se debe simular fallo
    if config['simulate_failure']:
        log_message("WARNING", "🧪 SIMULATE_FAILURE is enabled - Consumer will fail intentionally")
        log_message("ERROR", "💥 Simulated failure - Consumer exiting...")
        sys.exit(1)
    
    log_message("INFO", "=" * 50)
    
    success_count = 0
    error_count = 0
    
    try:
        while True:
            success, message = test_api_connection(config['api_url'], config['debug'])
            
            if success:
                success_count += 1
                log_message("SUCCESS", f"{message} (Total successful: {success_count})")
            else:
                error_count += 1
                log_message("ERROR", f"{message} (Total errors: {error_count})")
            
            # Mostrar estadísticas cada 10 intentos en modo debug
            if config['debug'] and (success_count + error_count) % 10 == 0:
                total = success_count + error_count
                success_rate = (success_count / total) * 100 if total > 0 else 0
                log_message("STATS", f"Success rate: {success_rate:.1f}% ({success_count}/{total})")
            
            sleep(config['delay'])
            
    except KeyboardInterrupt:
        log_message("INFO", "🛑 Consumer stopped by user")
        log_message("INFO", f"📊 Final stats - Success: {success_count}, Errors: {error_count}")
        sys.exit(0)
    except Exception as error:
        log_message("FATAL", f"💥 Unexpected error: {str(error)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

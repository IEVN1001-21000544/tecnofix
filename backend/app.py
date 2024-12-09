from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pymysql

app = Flask(__name__)

CORS(app)  # Permite cualquier dominio temporalmente


# Configura tu conexión a la base de datos
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='tecnofix'
    )

# Ruta para el login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='tecnofix'
        )
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM usuarios WHERE correo = %s"
        cursor.execute(query, (correo,))
        user = cursor.fetchone()

        if user and user['contrasena'] and check_password_hash(user['contrasena'], contrasena):
            return jsonify({
                'message': 'Login exitoso',
                'nombre': user['nombre'],
                'rol': user['rol']
            }), 200
        else:
            return jsonify({'message': 'Credenciales incorrectas'}), 401
    except Exception as e:
        print("Error:", str(e))  # Log de errores
        return jsonify({'message': 'Error al iniciar sesión', 'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Ruta para registrar usuarios
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    nombre = data.get('nombre')
    apellidop = data.get('apellidop')
    apellidom = data.get('apellidom')
    correo = data.get('correo')
    contrasena = data.get('contrasena')
    rol = data.get('rol')

    hashed_password = generate_password_hash(contrasena, method='pbkdf2:sha256')

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='tecnofix'
        )
        cursor = conn.cursor()

        query = """
        INSERT INTO usuarios (nombre, apellidop, apellidom, correo, contrasena, rol)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, apellidop, apellidom, correo, hashed_password, rol))
        conn.commit()

        return jsonify({'message': 'Usuario registrado exitosamente'}), 201
    except Exception as e:
        print("Error:", str(e))  # Log de errores
        return jsonify({'message': 'Error al registrar usuario', 'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

#Ruta de evento
@app.route('/api/events', methods=['GET'])
def get_events():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='tecnofix'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT event_name, event_type, SUM(event_count) AS count FROM events GROUP BY event_name, event_type")
    events = cursor.fetchall()
    connection.close()

    # Transformar datos
    data = {
        "user_login": sum(event['count'] for event in events if event['event_type'] == 'login'),
        "download_clicks": sum(event['count'] for event in events if event['event_type'] == 'download'),
        "tienda_clicks_info": sum(event['count'] for event in events if event['event_type'] == 'tienda'),
        "paquetes_clicks": sum(event['count'] for event in events if event['event_type'] == 'paquetes'),
        "tutoriales_clicks": sum(event['count'] for event in events if event['event_type'] == 'tutoriales'),
        "tutorialesInfo_clicks": sum(event['count'] for event in events if event['event_type'] == 'tutorialesInfo'),
        "herramientas_clicks": sum(event['count'] for event in events if event['event_type'] == 'herramientas'),
        "herramientasInfo_clicks": sum(event['count'] for event in events if event['event_type'] == 'herramientasInfo'),
    
    }
    return jsonify(data)



# Ruta para registrar un evento
@app.route('/api/events', methods=['POST'])
def register_event():
    try:
        # Obtener datos del cuerpo de la solicitud
        event_data = request.get_json()
        event_name = event_data.get('event_name')
        event_type = event_data.get('event_type')
        event_count = event_data.get('event_count', 1)  # Por defecto, 1

        # Conectar a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        # Guardar evento en la base de datos
        cursor.execute("""
            INSERT INTO events (event_name, event_type, event_count, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (event_name, event_type, event_count))
        connection.commit()

        # Cerrar conexión
        cursor.close()
        connection.close()

        return jsonify({'message': 'Evento registrado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, origins=["http://localhost:8081"])

def get_db_connection():
    conn = sqlite3.connect('operators.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/operators', methods=['GET'])
def get_operators():
    conn = get_db_connection()
    operators = conn.execute('SELECT * FROM operators').fetchall()
    conn.close()

    # Converte os registros para uma lista de dicionários
    operators_list = []
    for operator in operators:
        operators_list.append({
            "name": operator["name"],
            "images_background": operator["images_background"],
            "images_logo": operator["images_logo"],
            "link": operator["link"],
            "side": operator["side"],
            "squad": operator["squad"],
            "specialities": operator["specialities"],
            "health": operator["health"],
            "speed": operator["speed"],
            "primary_weapon": operator["primary_weapon"],
            "secundary_weapon": operator["secundary_weapon"],
            "gadget": operator["gadget"],
            "unique_ability": operator["unique_ability"]
        })

    return jsonify(operators_list)

@app.route('/operators/<string:operator_name>', methods=['GET'])
def get_operator(operator_name):
    conn = get_db_connection()
    operator = conn.execute('SELECT * FROM operators WHERE name = ?', (operator_name,)).fetchone()
    conn.close()

    if operator is None:
        return jsonify({'error': 'Operator not found'}), 404

    operator_data = {
        "name": operator["name"],
        "images_background": operator["images_background"],
        "images_logo": operator["images_logo"],
        "link": operator["link"],
        "side": operator["side"],
        "squad": operator["squad"],
        "specialities": operator["specialities"],
        "health": operator["health"],
        "speed": operator["speed"],
        "primary_weapon": operator["primary_weapon"],
        "secundary_weapon": operator["secundary_weapon"],
        "gadget": operator["gadget"],
        "unique_ability": operator["unique_ability"]
    }

    return jsonify(operator_data)

@app.route('/login', methods=['GET'])
def login_user():
    email = request.headers.get('email')
    password = request.headers.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e password são obrigatorios'}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
    # user = (email == "admin" and password == "admin")
    conn.close()

    if user:
        return jsonify({'message': 'Login feito', 'user': {'email': email}})
    else:
        return jsonify({'error': 'Credenciais invalidas'}), 401

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e password são obrigatorios'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifica se o utilizador já existe
    existing_user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({'error': 'User já existe'}), 400

    # Insere o novo utilizador
    cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                   (username, email, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Registration successful', 'user': {'email': email}}), 201


@app.route('/favorites', methods=['POST'])
def toggle_favorite():
    data = request.json
    email = data.get('email')
    operator_name = data.get('operator_name')

    if not email or not operator_name:
        return jsonify({'error': 'Email e operator_name são obrigatórios'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'Usuário não encontrado'}), 404

    user_id = user['id']

    # Verifica se o favorito já existe na base de dados
    existing = cursor.execute('SELECT * FROM favorites WHERE user_id = ? AND operator_name = ?',
                              (user_id, operator_name)).fetchone()

    if existing:
        # Se existir, remove o registro
        cursor.execute('DELETE FROM favorites WHERE user_id = ? AND operator_name = ?', (user_id, operator_name))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Favorite removed'})
    else:
        # Caso não exista, adiciona o registro na tabela de favoritos
        cursor.execute('INSERT INTO favorites (user_id, operator_name) VALUES (?, ?)', (user_id, operator_name))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Favorite added'})

@app.route('/favorites/<string:email>', methods=['GET'])
def get_favorites(email):
    conn = get_db_connection()
    favorites = conn.execute('SELECT operator_name FROM favorites WHERE user_id = (SELECT id FROM users WHERE email = ?)', (email,)).fetchall()
    conn.close()
    return jsonify([row['operator_name'] for row in favorites])


def main_api():
    app.run(debug=True, use_reloader=False)

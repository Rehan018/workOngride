import sqlite3
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/api/users', methods=['GET'])
def get_users_by_first_name():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        cursor.fetchall()
    except sqlite3.OperationalError:
        # Create the 'user' table if it doesn't exist
        cursor.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                age INTEGER,
                gender TEXT,
                email TEXT,
                phone TEXT,
                birth_date TEXT
            )
        ''')

    first_name = request.args.get('first_name')
    if not first_name:
        return jsonify({'error': 'Missing required parameter: first_name'}), 400
    
    cursor.execute("SELECT * FROM user WHERE first_name LIKE ?", ('%' + first_name + '%',))
    users = cursor.fetchall()
    
    if not users:
        url = f'https://dummyjson.com/users/search?q={first_name}'
        response = requests.get(url)
        if response.status_code == 200:
            external_users = response.json()
            if isinstance(external_users, list):
                # Insert the external users into the 'user' table
                for user in external_users:
                    cursor.execute("INSERT INTO user (first_name, last_name, age, gender, email, phone, birth_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (user['first_name'], user['last_name'], user['age'], user['gender'], user['email'], user['phone'], user['birth_date']))
            
                conn.commit()
                
                cursor.execute("SELECT * FROM user WHERE first_name LIKE ?", ('%' + first_name + '%',))
                users = cursor.fetchall()
        else:
            conn.close()
            return jsonify({'message': 'No users found with the given first name'}), 404
    
    conn.close()
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True)

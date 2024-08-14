import os
import csv
import mysql.connector
import shutil
import time
from flask import Flask, request, jsonify
import threading

class Database:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.connection = None
        self.cursor = None

    def conexiune(self):
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db
            )
            self.cursor = self.connection.cursor()

    def executeConexiune(self, query, values=None):
        self.conexiune()
        try:
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Eroare: {err}")
            self.connection.rollback()

    def fetchAll(self, query, values=None):
        self.conexiune()
        self.cursor.execute(query, values or ())
        return self.cursor.fetchall()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()

class ManagerFisiere:
    def __init__(self, backup_folder, folder_entries):
        self.backup_folder = backup_folder
        self.folder_entries = folder_entries
        self.ensure_directories()
        self.create_test_files()  # Crează fișierele de test pentru testare

    def ensure_directories(self):
        """ Asigură că directoarele necesare există. """
        if not os.path.exists(self.backup_folder):
            print(f"Creare folder de backup: {self.backup_folder}")
            os.makedirs(self.backup_folder)
        else:
            print(f"Folderul de backup există deja: {self.backup_folder}")

        if not os.path.exists(self.folder_entries):
            print(f"Creare folder pentru intrări: {self.folder_entries}")
            os.makedirs(self.folder_entries)
        else:
            print(f"Folderul pentru intrări există deja: {self.folder_entries}")

    def create_test_files(self):
        """ Crează fișiere de test în folderul de intrări. """
        files_data = {
            'Poarta1.csv': [
                '2024-08-13 08:00:00',
                '2024-08-13 09:30:00',
                '2024-08-13 12:00:00',
                '2024-08-13 15:45:00',
            ],
            'Poarta2.txt': [
                '2024-08-13 10:00:00',
                '2024-08-13 11:30:00',
                '2024-08-13 13:15:00',
                '2024-08-13 17:00:00',
            ],
        }

        for file_name, lines in files_data.items():
            file_path = os.path.join(self.folder_entries, file_name)
            if not os.path.exists(file_path):  
                with open(file_path, 'w') as file:
                    for line in lines:
                        file.write(f"{line}\n")
                print(f"Fișier creat: {file_path}")

    def Filemanager(self, db):
        while True:
            entry_files = os.listdir(self.folder_entries)
            print(f"Fișiere în folderul de intrări: {entry_files}")
            if not entry_files:
                print("Nu sunt fișiere de procesat.")
            for file in entry_files:
                file_path = os.path.join(self.folder_entries, file)
                if os.path.isfile(file_path):
                    nume_poarta, extensie = os.path.splitext(file)
                    if nume_poarta.startswith('Poarta'):
                        try:
                            nume_poarta_int = int(nume_poarta.replace('Poarta', ''))
                            if extensie in ['.csv', '.txt']:
                                print(f"Procesare fișier: {file}")
                                with open(file_path, 'r') as fisier:
                                    reader = csv.reader(fisier)
                                    for row in reader:
                                        if row:  # Asigură-te că rândul nu este gol
                                            print(f"Adăugare în baza de date: {row[0]}")
                                            query = 'INSERT INTO access (numar_poarta, tip_fisier, data_acces) VALUES (%s, %s, %s)'
                                            values = (nume_poarta_int, extensie[1:], row[0])  # Elimină punctul din extensie
                                            db.executeConexiune(query, values)
                                # Mută fișierul după procesare
                                backup_path = os.path.join(self.backup_folder, file)
                                shutil.move(file_path, backup_path)
                                print(f"Mutat fișierul {file} în folderul de backup.")
                        except Exception as e:
                            print(f"Eșec la procesarea fișierului {file}: {str(e)}")
            time.sleep(20)  # Așteaptă 20 de secunde înainte de a verifica din nou

class PoartaFisiereIntrari:
    def __init__(self, backup_folder, folder_entries):
        self.file_manager = ManagerFisiere(backup_folder, folder_entries)
        self.db = Database(host='localhost', user='root', password='root', db='in_outs')
        self.db.executeConexiune("""
            CREATE TABLE IF NOT EXISTS access (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numar_poarta INT NOT NULL,
                tip_fisier VARCHAR(45) NOT NULL,
                data_acces DATETIME NOT NULL
            )
        """)

    def rulare(self):
        threading.Thread(target=self.file_manager.Filemanager, args=(self.db,), daemon=True).start()

app = Flask(__name__)

@app.route('/start', methods=['GET'])
def start():
    try:
        procesareFisier = PoartaFisiereIntrari(backup_folder='backup_intrari', folder_entries='intrari')
        procesareFisier.rulare()
        return jsonify({"mesaj": "Procesul a început cu succes"}), 200
    except Exception as e:
        return jsonify({"eroare": f"Ceva nu a mers cum trebuie: {str(e)}"}), 500

@app.route('/Poarta4', methods=['POST'])
def JSONFile():
    try:
        input = request.json
        required_keys = ['data', 'sens', 'idPersoana', 'idPoarta']
        for key in required_keys:
            if key not in input:
                return jsonify({"eroare": f"Valoare negăsită pentru cheia '{key}'!"}), 400
        
        conn = mysql.connector.connect(host='localhost', user='root', password='root', database='virtuals')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO poarta2 (data, sens, idPersoana, idPoarta)
            VALUES (%s, %s, %s, %s)
        """, (input['data'], input['sens'], input['idPersoana'], input['idPoarta']))
        conn.commit()
        conn.close()
        return jsonify({"mesaj": "Perfect, date adăugate!"}), 200

    except Exception as e:
        return jsonify({"eroare": f"Ceva nu a mers cum trebuie: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

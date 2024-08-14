import os
import csv
import mysql.connector
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from abc import ABC, abstractmethod

class BazaDeDate:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host, user=self.user, password=self.password, database=self.database)
            self.cursor = self.connection.cursor()
            print("Conexiune la baza de date stabilită.")
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")

    def executeConnection(self, query, values=None):
        self.connect()
        if self.connection and self.cursor:
            try:
                if values:
                    self.cursor.execute(query, values)
                else:
                    self.cursor.execute(query)
                self.connection.commit()
            except mysql.connector.Error as err:
                print(f"Error: {err}")
            finally:
                self.close()
        else:
            print("Connection or cursor not initialized")

    def resultConnection(self, query, values=None):
        self.connect()
        if self.connection and self.cursor:
            try:
                if values:
                    self.cursor.execute(query, values)
                else:
                    self.cursor.execute(query)
                result = self.cursor.fetchall()
                self.connection.commit()
                return result
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                return []
            finally:
                self.close()
        else:
            print("Connection or cursor not initialized")
            return []

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

class InitiereBazaDate(ABC):
    def __init__(self, db):
        self.db = db


class Prezenta:
    def __init__(self, db_connection):
        self.db = db_connection

    def oreDeLucru(self, data):
        query = """
        SELECT idPersoana, MIN(data) as intrare, MAX(data) as iesire
        FROM virtuals
        WHERE DATE(data) = %s AND sens IN ('intrare', 'iesire')
        GROUP BY idPersoana
        """
        rezultatConexiune = self.db.resultConnection(query, (data,))
        ore_lucrate = {}
        for row in rezultatConexiune:
            id_Persoana, entry, exits = row
            if isinstance(entry, str):
                entry = datetime.strptime(entry, '%Y-%m-%d %H:%M:%S')
            if isinstance(exits, str):
                exits = datetime.strptime(exits, '%Y-%m-%d %H:%M:%S')
            if isinstance(entry, datetime) and isinstance(exits, datetime):
                worked_hours = (exits - entry).total_seconds() / 3600
                ore_lucrate[id_Persoana] = worked_hours
        return ore_lucrate

    def Notificari(self, ore_lucrate, ore_necesare):
        iduri = tuple(ore_lucrate.keys())
        if not iduri:
            return [], []

        query = "SELECT id, nume FROM users WHERE id IN (%s)" % ','.join(['%s'] * len(iduri))
        rezultatConexiune = self.db.resultConnection(query, iduri)

        angajatiNotificati = []
        angajatiSilitori = []
        for row in rezultatConexiune:
            id, nume = row
            detalii = {
                'nume': nume,
                'ore_lucrate': ore_lucrate.get(id, 0)
            }
            if ore_lucrate.get(id, 0) < ore_necesare:
                angajatiNotificati.append(detalii)
            elif ore_lucrate.get(id, 0) >= ore_necesare:
                angajatiSilitori.append(detalii)
        return angajatiNotificati, angajatiSilitori

class GeneratorDeRapoarte:
    def __init__(self, folder_backup):
        self.folder_backup = folder_backup
        if not os.path.exists(folder_backup):
            os.makedirs(folder_backup)

    def generareRapoarte(self, angajatiNotificati, angajatiSilitori):
        dataCurenta = datetime.now().strftime('%Y-%m-%d')
        fisierCSV_notificari = os.path.join(self.folder_backup, f'{dataCurenta}_chiulangii.csv')
        fisierTXT_notificari = os.path.join(self.folder_backup, f'{dataCurenta}_chiulangii.txt')
        fisierCSV_silitori = os.path.join(self.folder_backup, f'{dataCurenta}_silitori.csv')
        fisierTXT_silitori = os.path.join(self.folder_backup, f'{dataCurenta}_silitori.txt')

      
        with open(fisierCSV_notificari, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nume', 'Ore Lucrate'])
            for detalii in angajatiNotificati:
                writer.writerow([detalii['nume'], detalii['ore_lucrate']])
        
        with open(fisierTXT_notificari, 'w', encoding='utf-8') as file:
            for detalii in angajatiNotificati:
                file.write(f"Nume: {detalii['nume']}, Ore Lucrate: {detalii['ore_lucrate']}\n")

        
        with open(fisierCSV_silitori, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nume', 'Ore Lucrate'])
            for detalii in angajatiSilitori:
                writer.writerow([detalii['nume'], detalii['ore_lucrate']])

        with open(fisierTXT_silitori, 'w', encoding='utf-8') as file:
            for detalii in angajatiSilitori:
                file.write(f"Nume: {detalii['nume']}, Ore Lucrate: {detalii['ore_lucrate']}\n")

        print(f"Rapoarte generate în '{self.folder_backup}'.")

class TrimitereNotificari:
    def __init__(self, email_trimitator, email_parola):
        self.email_trimitator = email_trimitator
        self.email_parola = email_parola
        self.email_destinatar = 'petrucretu03@yahoo.com'  # Adresa constantă pentru toate notificările

    def notificareAngajat(self, angajatiNotificati, angajatiSilitori):
        for angajat in angajatiNotificati:
            self.trimiteEmail(angajat, tip="chiulangii")
        
        for angajat in angajatiSilitori:
            self.trimiteEmail(angajat, tip="silitori")

    def trimiteEmail(self, angajat, tip):
        nume = angajat['nume']
        
        if tip == "chiulangii":
            subiect = "Ore de lucru insuficiente"
            mesaj = f"Bună ziua {nume},\n\nConform înregistrărilor noastre, în această săptămână nu ați îndeplinit orele necesare de lucru.\nVă rugăm să vă conformați programului de lucru.\n\nMulțumim!"
        elif tip == "silitori":
            subiect = "Bonus pentru ore suplimentare"
            mesaj = f"Bună ziua {nume},\n\nVă informăm că ați lucrat un număr suficient de ore și veți primi un bonus pentru munca depusă!\n\nFelicitări și continuați munca bună!"
        else:
            subiect = "Notificare"
            mesaj = f"Bună ziua {nume},\n\nAcesta este un mesaj standard.\n\nMulțumim!"

        msg = MIMEMultipart()
        msg['From'] = self.email_trimitator
        msg['To'] = self.email_destinatar
        msg['Subject'] = subiect
        msg.attach(MIMEText(mesaj, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_trimitator, self.email_parola)
                server.send_message(msg)
            print(f"Notificare trimisă pentru angajatul {nume}, tip: {tip}")
        except Exception as e:
            print(f"Eroare la trimiterea emailului pentru {nume}: {e}")

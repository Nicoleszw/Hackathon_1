import requests
import psycopg2
import json
import random
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv('HOSTNAME')
DB_NAME = os.getenv('DATABASE')
DB_USER = os.getenv('NAME')
DB_PASSWORD = os.getenv('PASSWORD')
DB_PORT = os.getenv('PORT')

connection = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

# Retrieve the connection string from the environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

connection = psycopg2.connect(DATABASE_URL)

cursor = connection.cursor()
cursor.execute('DROP TABLE IF EXISTS trivia')

cursor.execute('''CREATE TABLE trivia
               (id SERIAL PRIMARY KEY, 
               question TEXT UNIQUE, 
               correct_answer TEXT)''')

connection.commit()

countries_api = requests.get('https://opentdb.com/api.php?amount=20')
data = countries_api.json()

print('table was created')
import psycopg2
import random

# Соединение с базой данных
conn = psycopg2.connect(
    host="77.105.167.59",
    database="projectdb",
    user="haryuuno",
    password="Pe59%YARD228339#"
)
cursor = conn.cursor()

for i in range(1,100):
    photo_url = f"https://www.gutenberg.org/cache/epub/{i}/pg{i}.cover.medium.jpg"
    cursor.execute(f"update book set photo_url = '{photo_url}' where id={i}")

conn.commit()
cursor.close()
conn.close()
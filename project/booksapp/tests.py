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

for i in range(9,100):
    random_double = round(random.uniform(1, 5),2)
    cursor.execute(f"INSERT INTO book values({i},'книга{i}','автор{i}','описание{i}','тег3',{random_double})")

conn.commit()
cursor.close()
conn.close()
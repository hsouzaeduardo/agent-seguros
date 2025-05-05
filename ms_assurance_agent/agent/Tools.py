import psycopg2
import os
import uuid
from openai import AzureOpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def save_conversation(session_id: str, role: str, message: str, username: str, stage: str):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO public.conversation_history (session_id, role, message, "timestamp", username, STAGE)
        values (%s, %s, %s, %s, %s, %s)
        
    """
    cursor.execute(query, (session_id, role, message, datetime.now(), username, stage))

    conn.commit()
    cursor.close()
    conn.close()

def connect_to_db():
    conn = psycopg2.connect(
        host= os.getenv("HOST"),
        database=os.getenv("database"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        port=os.getenv("port"),
        sslmode= os.getenv("sslmode")
    )
    print()
    return conn

# Função de busca de cliente
def get_customer(cpf: str, placa: str = "") -> str:
    conn = connect_to_db()
    cursor = conn.cursor()
    print("cpf", cpf)
    print("placa", placa)
    query = """
        SELECT name, address, phone, email, order_date, typeOfInsurance, status, total
        FROM customer
        INNER JOIN Insurance
        ON customer.id = Insurance.customer_id
        WHERE document = %s
        AND typeOfInsurance = 'Life Insurance';
    """
    cursor.execute(query, (cpf, ))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()

    if cliente:
        nome, address, telefone, email, order_date, typeOfInsurance, status, total = cliente
        return f"Nome: {nome}, Email: {email}, Telefone: {telefone}, Endereço: {address}, Seguro: {typeOfInsurance}, Status: {status}, Valor: {total}"
    else:
        return "Cliente não encontrado."

def save_image_relation(session_id, image_url):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO image_uploads (session_id, image_url, timestamp)
        VALUES (%s, %s, %s)
    """, (session_id, image_url, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
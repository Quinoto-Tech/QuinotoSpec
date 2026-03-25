import sqlite3
import os
import sys
import hashlib
import argparse
from datetime import datetime

def record_engram(content, type_val, prefix=None, db_path="engram.db"):
    if not os.path.exists(db_path):
        # Intentar en .quinoto-spec/ si no existe en el actual
        alt_path = os.path.join(".quinoto-spec", "engram.db")
        if os.path.exists(alt_path):
            db_path = alt_path
        else:
            print(f"Error: No se encontró la base de datos en {db_path} ni en {alt_path}")
            print("Por favor, inicializa la base de datos primero.")
            return False

    # Generar hash para evitar duplicados
    hash_input = f"{type_val}:{prefix or ''}:{content}"
    content_hash = hashlib.sha256(hash_input.encode()).hexdigest()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insertar en la tabla principal
        sql = """
        INSERT INTO engrams (type, prefix, content, hash)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(sql, (type_val, prefix, content, content_hash))
        
        conn.commit()
        print(f"Su sucesos: Recuerdo grabado en {db_path} con éxito.")
        return True

    except sqlite3.IntegrityError:
        print("Aviso: El recuerdo ya existe (hash duplicado).")
        return True
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Graba un nuevo recuerdo (engram) en la base de datos.")
    parser.add_argument("--content", required=True, help="El contenido del hallazgo o decisión")
    parser.add_argument("--type", required=True, choices=['decision', 'architecture', 'bug_fix', 'lesson'], help="Categoría del recuerdo")
    parser.add_argument("--prefix", help="Prefijo de propuesta (ej. AUTH)")
    parser.add_argument("--db", default="engram.db", help="Ruta a la base de datos")

    args = parser.parse_args()
    
    # Intentar detectar .quinoto-spec/engram.db por defecto si existe
    target_db = args.db
    if target_db == "engram.db" and not os.path.exists(target_db):
        if os.path.exists(".quinoto-spec/engram.db"):
            target_db = ".quinoto-spec/engram.db"

    record_engram(args.content, args.type, args.prefix, target_db)

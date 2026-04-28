import sqlite3
import sys
import os

def search_memory(query, db_path="engram.db"):
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos de memoria en {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Búsqueda usando FTS5 en la tabla virtual engrams_search
        sql = """
        SELECT e.timestamp, e.type, e.prefix, e.content
        FROM engrams e
        JOIN engrams_search es ON e.id = es.rowid
        WHERE engrams_search MATCH ?
        ORDER BY rank;
        """
        
        cursor.execute(sql, (query,))
        results = cursor.fetchall()

        if not results:
            print(f"No se encontraron recuerdos para: '{query}'")
            return

        print(f"# Resultados de búsqueda en Memoria: '{query}'\n")
        for row in results:
            timestamp, type_val, prefix, content = row
            prefix_str = f"[{prefix}] " if prefix else ""
            print(f"### {timestamp} | {type_val.upper()}")
            print(f"**Contexto:** {prefix_str}{content}\n")
            print("---")

    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python search.py \"termino de busqueda\"")
    else:
        search_query = sys.argv[1]
        # Intentamos encontrar la DB en el directorio actual o en .quinoto-spec/
        target_db = "engram.db"
        if not os.path.exists(target_db):
            target_db = os.path.join(".quinoto-spec", "engram.db")
        
        search_memory(search_query, target_db)

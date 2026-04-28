import sqlite3
import os
import sys

def init_database(db_path=".quinoto-spec/engram.db"):
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    if os.path.exists(db_path):
        print(f"La base de datos ya existe en {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Schema definition from documentation
        schema = """
        -- Tabla principal de hallazgos y decisiones
        CREATE TABLE engrams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            type TEXT NOT NULL, -- 'decision', 'architecture', 'bug_fix', 'lesson'
            prefix TEXT,        -- Referencia al prefijo de propuesta (ej. AUTH)
            content TEXT NOT NULL,
            hash TEXT UNIQUE    -- Para prevenir duplicados y facilitar la sincronización Git
        );

        -- Tabla de búsqueda virtual (FTS5) para búsqueda de texto completo
        CREATE VIRTUAL TABLE engrams_search USING fts5(
            content,
            prefix,
            content='engrams',
            content_rowid='id'
        );

        -- Triggers para mantener sincronizada la tabla FTS5
        CREATE TRIGGER engrams_ai AFTER INSERT ON engrams BEGIN
          INSERT INTO engrams_search(rowid, content, prefix) VALUES (new.id, new.content, new.prefix);
        END;
        """
        
        cursor.executescript(schema)
        conn.commit()
        print(f"Base de datos Engram inicializada con éxito en {db_path}")

    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    target_db = ".quinoto-spec/engram.db"
    # Si no existe .quinoto-spec, intentamos en el directorio actual
    if not os.path.exists(".quinoto-spec") and not os.path.exists(os.path.dirname(target_db)):
        target_db = "engram.db"
    
    init_database(target_db)

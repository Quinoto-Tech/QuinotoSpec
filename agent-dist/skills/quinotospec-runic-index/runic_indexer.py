import os
import chromadb
from chromadb.config import Settings
import re

class RunicIndexer:
    def __init__(self, project_root):
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".quinoto-spec", "memory")
        os.makedirs(self.db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name="quinotospec_main")

    def chunk_markdown(self, content):
        """Splits markdown by headers (H1, H2, H3)"""
        chunks = []
        headers = list(re.finditer(r'^(#+)\s+(.+)$', content, re.MULTILINE))
        
        last_pos = 0
        for i, match in enumerate(headers):
            if i > 0:
                chunks.append(content[last_pos:match.start()].strip())
            last_pos = match.start()
        
        chunks.append(content[last_pos:].strip())
        return [c for c in chunks if c]

    def chunk_code(self, content, file_ext):
        """Basic code chunking by classes/functions for Python/JS"""
        if file_ext in ['.py']:
            pattern = r'^(class|def)\s+\w+'
        elif file_ext in ['.js', '.ts']:
            pattern = r'^(function|class|const\s+\w+\s*=\s*(async\s*)?\([^)]*\)\s*=>)'
        else:
            return [content] # Default to no chunking or line-based

        chunks = []
        breaks = list(re.finditer(pattern, content, re.MULTILINE))
        
        last_pos = 0
        for i, match in enumerate(breaks):
            if i > 0:
                chunks.append(content[last_pos:match.start()].strip())
            last_pos = match.start()
        
        chunks.append(content[last_pos:].strip())
        return [c for c in chunks if c]

    def index_file(self, file_path):
        rel_path = os.path.relpath(file_path, self.project_root)
        _, ext = os.path.splitext(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limpieza: Borrar fragmentos antiguos de este archivo para evitar duplicidad o "fantasmas"
            self.collection.delete(where={"source": rel_path})
            
            if ext == '.md':
                chunks = self.chunk_markdown(content)
            else:
                chunks = self.chunk_code(content, ext)
            
            is_archived = "__" in rel_path
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{rel_path}_{i}"
                self.collection.upsert(
                    documents=[chunk],
                    metadatas=[{
                        "source": rel_path, 
                        "type": "code" if ext != ".md" else "doc",
                        "archived": "True" if is_archived else "False"
                    }],
                    ids=[chunk_id]
                )
            print(f"Indexado: {rel_path} ({len(chunks)} fragmentos)")
        except Exception as e:
            print(f"Error indexando {rel_path}: {e}")

    def index_project(self):
        """Recursively indexes the entire project, respecting ignore rules."""
        ignore_dirs = {'.git', '.quinoto-spec', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
        ignore_exts = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz', '.pyc', '.exe', '.bin'}
        
        print(f"🚀 Iniciando indexación completa en: {self.project_root}")
        
        for root, dirs, files in os.walk(self.project_root):
            # Prune ignored directories but ALLOW .quinoto-spec/proposals
            rel_root = os.path.relpath(root, self.project_root)
            
            # Si estamos en la raíz o navegando carpetas normales
            if rel_root == ".":
                dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
                # Forzar la inclusión de .quinoto-spec para buscar proposals
                if '.quinoto-spec' in os.listdir(self.project_root):
                    dirs.append('.quinoto-spec')
            
            # Si estamos dentro de .quinoto-spec, solo permitimos proposals
            if rel_root == ".quinoto-spec":
                dirs[:] = [d for d in dirs if d == 'proposals']
            
            # Si estamos dentro de proposals, permitimos todo (vivos y archivos __)
            # No hace falta podar nada aquí
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                _, ext = os.path.splitext(file)
                if ext.lower() in ignore_exts:
                    continue
                
                file_path = os.path.join(root, file)
                self.index_file(file_path)

if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    abs_root = os.path.abspath(root)
    indexer = RunicIndexer(abs_root)
    indexer.index_project()
    print("✅ Indexación finalizada.")

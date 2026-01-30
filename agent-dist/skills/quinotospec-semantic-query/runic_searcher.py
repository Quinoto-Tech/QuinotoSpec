import os
import chromadb
from chromadb.config import Settings
import argparse

class RunicSearcher:
    def __init__(self, project_root):
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".quinoto-spec", "memory")
        
        if not os.path.exists(self.db_path):
            raise Exception("Runic Memory not found. Run indexer first.")
            
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_collection(name="quinotospec_main")

    def search(self, query, top_k=5):
        """Perform semantic search and return formatted results."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        formatted_output = []
        formatted_output.append(f"# 🏮 Runic Memory Results for: '{query}'\n")
        
        if not results['documents'][0]:
            formatted_output.append("_No se encontraron resultados relevantes._")
            return "\n".join(formatted_output)

        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            source = metadata.get('source', 'Unknown')
            type = metadata.get('type', 'Unknown')
            is_archived = metadata.get('archived') == "True"
            distance = results['distances'][0][i] if 'distances' in results else 0
            
            # Formato de bloque Markdown
            status_tag = " [🏮 ARCHIVADO]" if is_archived else ""
            formatted_output.append(f"### 📍 Source: `{source}`{status_tag} (Score: {1-distance:.2f})")
            if type == 'code':
                ext = os.path.splitext(source)[1].lstrip('.')
                formatted_output.append(f"```{ext}\n{doc}\n```\n")
            else:
                formatted_output.append(f"{doc}\n")
            
        return "\n".join(formatted_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runic Semantic Search")
    parser.add_argument("query", help="The natural language query")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return")
    
    args = parser.parse_args()
    
    try:
        abs_root = os.path.abspath(args.root)
        searcher = RunicSearcher(abs_root)
        print(searcher.search(args.query, top_k=args.top_k))
    except Exception as e:
        print(f"❌ Error: {e}")

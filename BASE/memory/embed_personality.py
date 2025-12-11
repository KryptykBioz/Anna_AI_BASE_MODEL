# Filename: BASE/memory/embed_personality.py
"""
Personality Training Data Embedder - Two-Stage Architecture
Separates training data into:
1. THOUGHT EXAMPLES - For thought processor (event interpretation, action planning)
2. RESPONSE EXAMPLES - For response generator (spoken output synthesis)

Usage: python embed_personality.py
"""

import sys
import json
import requests
import hashlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class PersonalityEmbedder:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.embed_model = "nomic-embed-text"
        
        script_dir = Path(__file__).resolve().parent
        base_dir = script_dir.parents[1]
        
        self.input_dir = base_dir / "personality" / "base_memory" / "base_personality"
        self.output_base = base_dir / "personality" / "base_memory" / "base_memories"
        self.thought_output_dir = self.output_base / "thought_examples"
        self.response_output_dir = self.output_base / "response_examples"
        
        print(f"DEBUG: Script dir: {script_dir}")
        print(f"DEBUG: Base dir: {base_dir}")
        print(f"DEBUG: Input dir: {self.input_dir}")
        print(f"DEBUG: Thought output: {self.thought_output_dir}")
        print(f"DEBUG: Response output: {self.response_output_dir}")
        print(f"DEBUG: Input exists: {self.input_dir.exists()}")
        
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'thought_chunks': 0,
            'response_chunks': 0,
            'total_embeddings': 0
        }
        
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Ollama."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.embed_model, "prompt": text},
                timeout=30
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def load_training_module(self, filepath: Path) -> Optional[Tuple[List[Dict], str, str]]:
        """
        Dynamically load a Python training file.
        
        Returns:
            (response_examples, system_prompt/system_context, processing_stage)
            processing_stage: 'thought' or 'response'
        """
        try:
            spec = importlib.util.spec_from_file_location("training_module", filepath)
            if not spec or not spec.loader:
                print(f"Could not load {filepath.name}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Try both variable names for examples
            examples = getattr(module, 'response_examples', None) or getattr(module, 'training_examples', None)
            
            # Try both variable names for system info
            system_info = getattr(module, 'system_prompt', None) or getattr(module, 'system_context', "AI assistant personality template")
            
            processing_stage = getattr(module, 'processing_stage', 'response')
            
            if not examples:
                print(f"[WARNING] {filepath.name}: No 'response_examples' or 'training_examples' found")
                return None
            
            print(f"[SUCCESS] Loaded {filepath.name}: {len(examples)} examples (stage: {processing_stage})")
            return examples, system_info, processing_stage
            
        except Exception as e:
            print(f"Error loading {filepath.name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_chunk(self, item: Dict, idx: int, source_file: str, stage: str) -> Dict[str, Any]:
        """
        Create chunk for either thought or response stage.
        Uses only: context, response, keywords, processing_stage
        """
        context = item.get('context', '')
        response = item.get('response', '')
        keywords = item.get('keywords', [])
        
        if not context or not response:
            return None
        
        # Create searchable text from context, response, and keywords
        searchable_parts = [context, response] + keywords
        searchable_text = ' '.join(searchable_parts)
        
        # Simple chunk format
        chunk_text = f"""CONTEXT: {context}

RESPONSE: {response}

KEYWORDS: {', '.join(keywords)}"""
        
        return {
            "text": chunk_text,
            "searchable_text": searchable_text,
            "metadata": {
                "type": f"{stage}_example",
                "stage": stage,
                "context": context,
                "response": response,
                "keywords": keywords,
                "source_file": source_file,
                "example_index": idx
            }
        }
    
    def create_stage_summary(self, examples: List[Dict], stage: str, 
                           system_info: str, source_file: str) -> Dict[str, Any]:
        """Create summary chunk including system prompt/context."""
        
        # Collect all keywords
        all_keywords = []
        for ex in examples:
            all_keywords.extend(ex.get('keywords', []))
        
        unique_keywords = list(set(all_keywords))
        top_keywords = unique_keywords[:20]  # Top 20 most common patterns
        
        summary_text = f"""SYSTEM INFO:
{system_info}

STAGE: {stage}
TOTAL EXAMPLES: {len(examples)}
KEY PATTERNS: {', '.join(top_keywords)}"""
        
        searchable = f"{system_info} {stage} {' '.join(top_keywords)}"
        
        return {
            "text": summary_text,
            "searchable_text": searchable,
            "metadata": {
                "type": "stage_summary",
                "stage": stage,
                "example_count": len(examples),
                "system_info": system_info,
                "source_file": source_file
            }
        }
    
    def process_training_file(self, examples: List[Dict], system_info: str, 
                             processing_stage: str, source_file: str) -> List[Dict]:
        """
        Process training data into chunks.
        All examples from one file share the same processing_stage.
        """
        chunks = []
        
        # Add system summary as first chunk
        summary = self.create_stage_summary(examples, processing_stage, system_info, source_file)
        chunks.append(summary)
        
        # Process each example
        for idx, item in enumerate(examples):
            chunk = self.create_chunk(item, idx, source_file, processing_stage)
            if chunk:
                chunks.append(chunk)
            else:
                print(f"[WARNING] Skipping malformed item {idx} in {source_file}")
        
        return chunks
    
    def embed_chunks(self, chunks: List[Dict[str, Any]], stage: str) -> List[Dict[str, Any]]:
        """Generate embeddings for chunks."""
        print(f"  Generating {stage} embeddings for {len(chunks)} chunks...")
        
        embedded_chunks = []
        for i, chunk in enumerate(chunks, 1):
            embed_text = chunk.get('searchable_text', chunk['text'])
            embedding = self.get_embedding(embed_text)
            
            if embedding:
                chunk['embedding'] = embedding
                chunk['hash'] = hashlib.md5(chunk['text'].encode()).hexdigest()
                chunk['char_count'] = len(chunk['text'])
                embedded_chunks.append(chunk)
                if i % 10 == 0:
                    print(f"    Progress: {i}/{len(chunks)}")
        
        failed = len(chunks) - len(embedded_chunks)
        print(f"  [SUCCESS] Successfully embedded {len(embedded_chunks)}/{len(chunks)} chunks")
        if failed:
            print(f"  [WARNING] Failed to embed {failed} chunks")
        
        self.stats['total_embeddings'] += len(embedded_chunks)
        return embedded_chunks
    
    def save_embeddings(self, chunks: List[Dict[str, Any]], stage: str, 
                       source_filename: str):
        """Save embedded chunks to appropriate directory."""
        base_name = Path(source_filename).stem
        
        # Determine output directory
        if stage == 'thought':
            output_dir = self.thought_output_dir
            suffix = "thought_examples"
        else:  # response
            output_dir = self.response_output_dir
            suffix = "response_examples"
        
        output_filename = f"{base_name}_{suffix}.json"
        output_path = output_dir / output_filename
        
        # Count unique keywords
        all_keywords = []
        for c in chunks:
            if 'metadata' in c and 'keywords' in c['metadata']:
                all_keywords.extend(c['metadata']['keywords'])
        unique_keywords = list(set(all_keywords))
        
        output_data = {
            "source_file": source_filename,
            "processing_stage": stage,
            "embed_model": self.embed_model,
            "total_chunks": len(chunks),
            "unique_keywords": len(unique_keywords),
            "chunks": chunks
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"  [SUCCESS] Saved {stage} to: {output_filename}")
        print(f"    Size: {output_path.stat().st_size / 1024:.1f} KB")
        print(f"    Unique keywords: {len(unique_keywords)}")
    
    def process_file(self, filepath: Path) -> bool:
        """Process a single training file."""
        print(f"Processing: {filepath.name}")
        
        result = self.load_training_module(filepath)
        if not result:
            return False
        
        examples, system_info, processing_stage = result
        
        print(f"  Creating training chunks for stage: {processing_stage}")
        chunks = self.process_training_file(examples, system_info, processing_stage, filepath.name)
        
        print(f"  Total chunks: {len(chunks)}")
        
        if processing_stage == 'thought':
            self.stats['thought_chunks'] += len(chunks)
        else:
            self.stats['response_chunks'] += len(chunks)
        
        # Embed chunks
        embedded_chunks = self.embed_chunks(chunks, processing_stage)
        if not embedded_chunks:
            return False
        
        # Save to appropriate directory
        self.save_embeddings(embedded_chunks, processing_stage, filepath.name)
        
        return True
    
    def process_all_files(self):
        """Process all Python training files in the input directory."""
        self.thought_output_dir.mkdir(parents=True, exist_ok=True)
        self.response_output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.input_dir.exists():
            print(f"Input directory does not exist: {self.input_dir}")
            return False
        
        python_files = [f for f in self.input_dir.glob("*.py") 
                       if not f.name.startswith('__') and not f.name.startswith('.')]
        
        if not python_files:
            print(f"No training files found in {self.input_dir}")
            return False
        
        self.stats['total_files'] = len(python_files)
        
        print(f"TWO-STAGE PERSONALITY EMBEDDER")
        print(f"Input directory: {self.input_dir}")
        print(f"Thought output: {self.thought_output_dir}")
        print(f"Response output: {self.response_output_dir}")
        print(f"Found {len(python_files)} training file(s) to process")
 
        
        for filepath in python_files:
            if self.process_file(filepath):
                self.stats['processed_files'] += 1
            else:
                self.stats['failed_files'] += 1
        
        self.print_summary()
        return self.stats['processed_files'] > 0
    
    def print_summary(self):
        """Print processing summary."""

        print(f"PROCESSING COMPLETE")
 
        print(f"Files found:       {self.stats['total_files']}")
        print(f"Files processed:   {self.stats['processed_files']}")
        print(f"Files failed:      {self.stats['failed_files']}")
        print(f"Thought chunks:    {self.stats['thought_chunks']}")
        print(f"Response chunks:   {self.stats['response_chunks']}")
        print(f"Total embeddings:  {self.stats['total_embeddings']}")
 
        
        if self.stats['processed_files'] > 0:
            print(f"\n[SUCCESS] Successfully processed {self.stats['processed_files']} personality file(s)")
            print(f"\nEmbedded files are ready:")
            print(f"  Thought examples: {self.thought_output_dir}")
            print(f"  Response examples: {self.response_output_dir}")
        else:
            print(f"\nNo files were successfully processed")

def check_ollama_available(ollama_url: str) -> bool:
    """Check if Ollama is running and model is available."""
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except:
        return False

def main():
    embedder = PersonalityEmbedder()
    
    print("Checking Ollama connection...")
    if not check_ollama_available(embedder.ollama_url):
        print("Cannot connect to Ollama")
        print("Please start Ollama with: ollama serve")
        sys.exit(1)
    print("[SUCCESS] Ollama is running")
    
    print(f"Testing embedding model '{embedder.embed_model}'...")
    test_embedding = embedder.get_embedding("test")
    if not test_embedding:
        print(f"Embedding model '{embedder.embed_model}' not available")
        print(f"Pull it with: ollama pull {embedder.embed_model}")
        sys.exit(1)
    print("[SUCCESS] Embedding model is ready\n")
    
    success = embedder.process_all_files()
    
    if success:
        print("\n[SUCCESS] Personality embeddings ready for use!")
        print("\nNext steps:")
        print("1. Restart your AI agent to load the new personality embeddings")
        print("2. The agent will automatically detect and load all personality files")
        print("3. Thought examples will be used during event interpretation")
        print("4. Response examples will be used during spoken output generation")
        print("5. Monitor logs to see stage-specific personality retrieval in action")
    else:
        print("\nEmbedding process failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
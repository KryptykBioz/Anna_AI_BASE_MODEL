# Filename: BASE/memory/memory_search.py
"""
ENHANCED: Combined User Input + Thought Chain Memory Retrieval
Memory search now considers both user input AND recent thoughts for relevance
"""

import numpy as np
from typing import List, Dict, Optional
from functools import lru_cache
from pathlib import Path
import json


class MemorySearch:
    """Memory search with combined query construction from user input + thoughts"""
    
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        
        # Embedding caches
        self._embedding_norms_cache = {}
        self._embeddings_cache = {}
        
        # Two-stage personality storage
        self._thought_examples = []
        self._response_examples = []
        
        # Load personality examples on initialization
        self._load_personality_examples()
    
    # ========================================================================
    # ENHANCED: COMBINED QUERY CONSTRUCTION
    # ========================================================================
    
    def build_combined_query(
        self,
        user_input: str = "",
        recent_thoughts: List[str] = None,
        weight_user: float = 0.6,
        weight_thoughts: float = 0.4
    ) -> str:
        """
        Build combined query from user input and recent thoughts
        
        Args:
            user_input: Current user input
            recent_thoughts: List of recent thought strings
            weight_user: Weight for user input (0.0-1.0)
            weight_thoughts: Weight for thoughts (0.0-1.0)
        
        Returns:
            Combined query string weighted appropriately
        """
        query_parts = []
        
        # Add user input (higher weight - it's explicit)
        if user_input and user_input.strip():
            # Repeat user input based on weight to increase its influence
            repetitions = max(1, int(weight_user * 10))
            for _ in range(repetitions):
                query_parts.append(user_input.strip())
        
        # Add recent thoughts (lower weight - they're implicit context)
        if recent_thoughts:
            # Take last 3-5 thoughts for context
            relevant_thoughts = recent_thoughts[-5:]
            repetitions = max(1, int(weight_thoughts * 10))
            
            for _ in range(repetitions):
                for thought in relevant_thoughts:
                    if thought and len(thought.strip()) > 10:  # Skip trivial thoughts
                        query_parts.append(thought.strip())
        
        # Combine into single query
        combined = " ".join(query_parts)
        
        # Truncate to reasonable length (embeddings work best with focused queries)
        if len(combined) > 500:
            combined = combined[:500]
        
        return combined
    
    def build_combined_embedding(
        self,
        user_input: str = "",
        recent_thoughts: List[str] = None,
        weight_user: float = 0.6,
        weight_thoughts: float = 0.4
    ) -> Optional[np.ndarray]:
        """
        Build weighted combined embedding from user input + thoughts
        
        This creates a hybrid embedding that represents both what the user
        said and what the agent has been thinking about recently.
        
        Args:
            user_input: Current user input
            recent_thoughts: List of recent thought strings
            weight_user: Weight for user input embedding
            weight_thoughts: Weight for thought embeddings
        
        Returns:
            Combined weighted embedding or None if failed
        """
        embeddings_to_combine = []
        weights = []
        
        # Get user input embedding
        if user_input and user_input.strip():
            user_embedding = self._get_query_embedding(user_input)
            if user_embedding is not None:
                embeddings_to_combine.append(user_embedding)
                weights.append(weight_user)
        
        # Get thought embeddings (average recent thoughts)
        if recent_thoughts:
            thought_embeddings = []
            
            for thought in recent_thoughts[-5:]:  # Last 5 thoughts
                if thought and len(thought.strip()) > 10:
                    thought_emb = self._get_query_embedding(thought)
                    if thought_emb is not None:
                        thought_embeddings.append(thought_emb)
            
            if thought_embeddings:
                # Average all thought embeddings into one
                avg_thought_embedding = np.mean(thought_embeddings, axis=0)
                embeddings_to_combine.append(avg_thought_embedding)
                weights.append(weight_thoughts)
        
        if not embeddings_to_combine:
            return None
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Compute weighted combination
        combined_embedding = np.zeros_like(embeddings_to_combine[0])
        for embedding, weight in zip(embeddings_to_combine, normalized_weights):
            combined_embedding += embedding * weight
        
        # Normalize the combined embedding
        norm = np.linalg.norm(combined_embedding)
        if norm > 1e-8:
            combined_embedding = combined_embedding / norm
        
        return combined_embedding
    
    # ========================================================================
    # ENHANCED: MEMORY SEARCH WITH COMBINED CONTEXT
    # ========================================================================
    
    def search_base_knowledge_combined(
        self,
        user_input: str = "",
        recent_thoughts: List[str] = None,
        k: int = 5,
        min_similarity: float = 0.3,
        use_embedding_combination: bool = True
    ) -> List[Dict]:
        """Search base knowledge using combined user input + thought context"""
        
        # Log usage of enhanced system
        if recent_thoughts and self.memory_manager.logger:
            self.memory_manager.logger.memory(
                f"[Enhanced Search] Base knowledge: "
                f"user_input={len(user_input)} chars, "
                f"thoughts={len(recent_thoughts)} items, "
                f"method={'embedding' if use_embedding_combination else 'text'}"
            )
        # Build query embedding based on method
        if use_embedding_combination:
            query_embedding = self.build_combined_embedding(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                weight_user=0.6,
                weight_thoughts=0.4
            )
        else:
            combined_query = self.build_combined_query(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                weight_user=0.6,
                weight_thoughts=0.4
            )
            query_embedding = self._get_query_embedding(combined_query)
        
        if query_embedding is None:
            return []
        
        chunks = self.memory_manager.base_knowledge
        
        if not chunks:
            return []
        
        embeddings = []
        valid_chunks = []
        
        for chunk in chunks:
            if 'embedding' in chunk and chunk['embedding']:
                embeddings.append(np.array(chunk['embedding'], dtype=np.float32))
                valid_chunks.append(chunk)
        
        if not embeddings:
            return []
        
        embeddings_matrix = np.vstack(embeddings)
        document_norms = self._precompute_norms(embeddings)
        similarities = self._vectorized_cosine_similarity(
            query_embedding,
            embeddings_matrix,
            document_norms
        )
        
        # Filter by minimum similarity
        valid_indices = np.where(similarities >= min_similarity)[0]
        
        if len(valid_indices) == 0:
            return []
        
        valid_similarities = similarities[valid_indices]
        top_k_local = self._top_k_argpartition(valid_similarities, min(k, len(valid_similarities)))
        top_k_indices = valid_indices[top_k_local]
        
        results = []
        for idx in top_k_indices:
            chunk = valid_chunks[idx]
            results.append({
                'text': chunk.get('text', ''),
                'metadata': chunk.get('metadata', {}),
                'similarity': float(similarities[idx]),
                'content_types': chunk.get('metadata', {}).get('content_types', [])
            })
        
        return results
    
    def search_long_memory_combined(
        self,
        user_input: str = "",
        recent_thoughts: List[str] = None,
        k: int = 5,
        use_embedding_combination: bool = True
    ) -> List[Dict]:
        """
        Search long-term memory using combined context
        
        Args:
            user_input: Current user input
            recent_thoughts: List of recent thought strings
            k: Number of results to return
            use_embedding_combination: Use weighted embedding vs text concatenation
        
        Returns:
            List of relevant summaries with similarity scores
        """
        if use_embedding_combination:
            query_embedding = self.build_combined_embedding(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                weight_user=0.6,
                weight_thoughts=0.4
            )
        else:
            combined_query = self.build_combined_query(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                weight_user=0.6,
                weight_thoughts=0.4
            )
            query_embedding = self._get_query_embedding(combined_query)
        
        if query_embedding is None:
            return []
        
        summaries = self.memory_manager.long_memory
        
        if not summaries:
            return []
        
        embeddings = []
        valid_summaries = []
        
        for summary in summaries:
            if 'embedding' in summary and summary['embedding']:
                embeddings.append(np.array(summary['embedding'], dtype=np.float32))
                valid_summaries.append(summary)
        
        if not embeddings:
            return []
        
        embeddings_matrix = np.vstack(embeddings)
        document_norms = self._precompute_norms(embeddings)
        similarities = self._vectorized_cosine_similarity(
            query_embedding,
            embeddings_matrix,
            document_norms
        )
        
        top_k_indices = self._top_k_argpartition(similarities, k)
        
        results = []
        for idx in top_k_indices:
            summary = valid_summaries[idx]
            results.append({
                'date': summary.get('date', ''),
                'summary': summary.get('summary', ''),
                'similarity': float(similarities[idx])
            })
        
        return results
    
    def search_medium_memory_combined(
        self,
        user_input: str = "",
        recent_thoughts: List[str] = None,
        k: int = 3,
        use_embedding_combination: bool = True
    ) -> List[Dict]:
        """
        Search medium-term memory using combined context
        
        Args:
            user_input: Current user input
            recent_thoughts: List of recent thought strings
            k: Number of results to return
            use_embedding_combination: Use weighted embedding vs text concatenation
        
        Returns:
            List of relevant messages with similarity scores
        """
        if use_embedding_combination:
            query_embedding = self.build_combined_embedding(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                weight_user=0.6,
                weight_thoughts=0.4
            )
        else:
            combined_query = self.build_combined_query(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                weight_user=0.6,
                weight_thoughts=0.4
            )
            query_embedding = self._get_query_embedding(combined_query)
        
        if query_embedding is None:
            return []
        
        messages = self.memory_manager.medium_memory
        
        if not messages:
            return []
        
        embeddings = []
        valid_messages = []
        
        for msg in messages:
            if 'embedding' in msg and msg['embedding']:
                embeddings.append(np.array(msg['embedding'], dtype=np.float32))
                valid_messages.append(msg)
        
        if not embeddings:
            return []
        
        embeddings_matrix = np.vstack(embeddings)
        document_norms = self._precompute_norms(embeddings)
        similarities = self._vectorized_cosine_similarity(
            query_embedding,
            embeddings_matrix,
            document_norms
        )
        
        top_k_indices = self._top_k_argpartition(similarities, k)
        
        results = []
        for idx in top_k_indices:
            msg = valid_messages[idx]
            results.append({
                'role': msg.get('role', ''),
                'content': msg.get('content', ''),
                'timestamp': msg.get('timestamp', ''),
                'similarity': float(similarities[idx])
            })
        
        return results
    
    # ========================================================================
    # BACKWARD COMPATIBILITY: Original methods preserved
    # ========================================================================
    
    def search_base_knowledge(self, query: str, k: int = 5, min_similarity: float = 0.3) -> List[Dict]:
        """Original method - preserved for backward compatibility"""
        return self.search_base_knowledge_combined(
            user_input=query,
            recent_thoughts=None,
            k=k,
            min_similarity=min_similarity,
            use_embedding_combination=False
        )
    
    def search_long_memory(self, query: str, k: int = 5) -> List[Dict]:
        """Original method - preserved for backward compatibility"""
        return self.search_long_memory_combined(
            user_input=query,
            recent_thoughts=None,
            k=k,
            use_embedding_combination=False
        )
    
    def search_medium_memory(self, query: str, k: int = 3) -> List[Dict]:
        """Original method - preserved for backward compatibility"""
        return self.search_medium_memory_combined(
            user_input=query,
            recent_thoughts=None,
            k=k,
            use_embedding_combination=False
        )
    
    # ========================================================================
    # TWO-STAGE PERSONALITY LOADING (Preserved)
    # ========================================================================
    
    def _load_personality_examples(self):
        """Load personality examples for both stages on startup"""
        try:
            project_root = self.memory_manager.project_root
            
            thought_dir = project_root / "personality" / "base_memory" / "base_memories" / "thought_examples"
            if thought_dir.exists():
                self._thought_examples = self._load_examples_from_directory(thought_dir)
                if self._thought_examples:
                    self.memory_manager.logger.memory(
                        f"[Personality] Loaded {len(self._thought_examples)} thought examples"
                    )
            
            response_dir = project_root / "personality" / "base_memory" / "base_memories" / "response_examples"
            if response_dir.exists():
                self._response_examples = self._load_examples_from_directory(response_dir)
                if self._response_examples:
                    self.memory_manager.logger.memory(
                        f"[Personality] Loaded {len(self._response_examples)} response examples"
                    )
            
            if not self._thought_examples and not self._response_examples:
                self.memory_manager.logger.warning(
                    "[Personality] No personality examples found. Run embed_personality.py to generate them."
                )
        
        except Exception as e:
            self.memory_manager.logger.error(f"[Personality] Failed to load examples: {e}")
    
    def _load_examples_from_directory(self, directory: Path) -> List[Dict]:
        """Load all personality example files from a directory"""
        examples = []
        
        try:
            json_files = list(directory.glob("*.json"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                    
                    chunks = file_data.get('chunks', [])
                    
                    for chunk in chunks:
                        if 'embedding' in chunk and isinstance(chunk['embedding'], list):
                            examples.append(chunk)
                
                except Exception as e:
                    self.memory_manager.logger.error(
                        f"[Personality] Failed to load {json_file.name}: {e}"
                    )
        
        except Exception as e:
            self.memory_manager.logger.error(f"[Personality] Directory load error: {e}")
        
        return examples
    
    def search_personality_examples(
        self,
        query: str,
        stage: str,
        k: int = 2,
        min_similarity: float = 0.35
    ) -> List[Dict]:
        """Search personality examples for a specific stage"""
        if stage == 'thought':
            examples = self._thought_examples
        elif stage == 'response':
            examples = self._response_examples
        else:
            self.memory_manager.logger.error(f"[Personality] Invalid stage: {stage}")
            return []
        
        if not examples:
            return []
        
        query_embedding = self._get_query_embedding(query)
        if query_embedding is None:
            return []
        
        embeddings = []
        valid_examples = []
        
        for ex in examples:
            if 'embedding' in ex and ex['embedding']:
                embeddings.append(np.array(ex['embedding'], dtype=np.float32))
                valid_examples.append(ex)
        
        if not embeddings:
            return []
        
        embeddings_matrix = np.vstack(embeddings)
        document_norms = self._precompute_norms(embeddings)
        similarities = self._vectorized_cosine_similarity(
            query_embedding,
            embeddings_matrix,
            document_norms
        )
        
        valid_indices = np.where(similarities >= min_similarity)[0]
        
        if len(valid_indices) == 0:
            return []
        
        valid_similarities = similarities[valid_indices]
        top_k_local = self._top_k_argpartition(valid_similarities, min(k, len(valid_similarities)))
        top_k_indices = valid_indices[top_k_local]
        
        results = []
        for idx in top_k_indices:
            ex = valid_examples[idx]
            results.append({
                'text': ex.get('text', ''),
                'searchable_text': ex.get('searchable_text', ''),
                'metadata': ex.get('metadata', {}),
                'similarity': float(similarities[idx]),
                'category': ex.get('metadata', {}).get('category', 'unknown')
            })
        
        return results
    
    def get_thought_processing_examples(self, situation: str, k: int = 2) -> str:
        """Get formatted thought processing examples"""
        examples = self.search_personality_examples(
            query=situation,
            stage='thought',
            k=k
        )
        
        if not examples:
            return ""
        
        formatted = []
        
        for ex in examples:
            text = ex['text']
            lines = text.split('\n')
            
            situation_text = ""
            cognition_text = ""
            
            for line in lines:
                if 'SITUATION:' in line:
                    situation_text = line.split('SITUATION:', 1)[1].strip()
                elif 'INTERNAL COGNITION:' in line:
                    cognition_text = line.split('INTERNAL COGNITION:', 1)[1].strip()
            
            if situation_text and cognition_text:
                formatted.append(f"SITUATION: {situation_text}")
                formatted.append(f"THOUGHT: {cognition_text}\n")
        
        if not formatted:
            return ""
        
        return "\n".join(formatted)
    
    def get_response_generation_examples(self, context: str, k: int = 2) -> str:
        """Get formatted response generation examples"""
        examples = self.search_personality_examples(
            query=context,
            stage='response',
            k=k
        )
        
        if not examples:
            return ""
        
        formatted = []
        
        for ex in examples:
            text = ex['text']
            lines = text.split('\n')
            
            situation_text = ""
            response_text = ""
            
            for line in lines:
                if 'SITUATION:' in line:
                    situation_text = line.split('SITUATION:', 1)[1].strip()
                elif 'RESPONSE:' in line or 'OUTPUT:' in line:
                    delimiter = 'RESPONSE:' if 'RESPONSE:' in line else 'OUTPUT:'
                    response_text = line.split(delimiter, 1)[1].strip()
            
            if situation_text and response_text:
                formatted.append(f"SITUATION: {situation_text}")
                formatted.append(f"RESPONSE: {response_text}\n")
        
        if not formatted:
            return ""
        
        return "\n".join(formatted)
    
    # ========================================================================
    # UTILITY METHODS (Preserved)
    # ========================================================================
    
    @lru_cache(maxsize=1000)
    def _get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Cache query embeddings for repeated searches"""
        embedding = self.memory_manager._get_ollama_embedding(query)
        if embedding is None:
            return None
        return np.array(embedding, dtype=np.float32)
    
    def _precompute_norms(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """Pre-compute norms for faster similarity calculation"""
        embeddings_matrix = np.vstack(embeddings).astype(np.float32)
        norms = np.linalg.norm(embeddings_matrix, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        return norms
    
    def _vectorized_cosine_similarity(
        self, 
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray,
        document_norms: np.ndarray
    ) -> np.ndarray:
        """Vectorized cosine similarity calculation"""
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        query_norm = np.linalg.norm(query_embedding)
        query_norm = max(query_norm, 1e-8)
        
        dot_products = document_embeddings @ query_embedding.T
        similarities = dot_products / (document_norms * query_norm)
        
        return similarities.flatten()
    
    def _top_k_argpartition(self, similarities: np.ndarray, k: int) -> np.ndarray:
        """Fast top-k selection using argpartition"""
        if len(similarities) <= k:
            return np.argsort(-similarities)
        
        top_k_indices = np.argpartition(-similarities, k)[:k]
        top_k_indices = top_k_indices[np.argsort(-similarities[top_k_indices])]
        
        return top_k_indices
    
    def get_short_memory(self) -> str:
        """Get formatted short memory"""
        if not self.memory_manager.short_memory:
            return ""
        
        lines = []
        for entry in self.memory_manager.short_memory[-10:]:
            role = (self.memory_manager.username if entry['role'] == 'user' 
                   else self.memory_manager.agentname)
            content = entry['content']
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def get_yesterday_context(self, max_entries: int = 10) -> str:
        """Get yesterday's conversation in full detail"""
        from datetime import datetime, timedelta
        
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        yesterday_entries = [
            e for e in self.memory_manager.medium_memory 
            if e.get('date') == yesterday
        ]
        
        if not yesterday_entries:
            return ""
        
        lines = []
        for entry in yesterday_entries[-max_entries:]:
            role = (self.memory_manager.username if entry['role'] == 'user' 
                   else self.memory_manager.agentname)
            content = entry['content']
            timestamp = entry.get('timestamp', '')
            lines.append(f"[{timestamp}] {role}: {content}")
        
        return "\n".join(lines)
    
    def reload_personality_examples(self):
        """Reload personality examples"""
        self._thought_examples = []
        self._response_examples = []
        self._load_personality_examples()
        self.memory_manager.logger.system("[Personality] Examples reloaded")
    
    def clear_caches(self):
        """Clear all caches to free memory"""
        self._get_query_embedding.cache_clear()
        self._embedding_norms_cache.clear()
        self._embeddings_cache.clear()
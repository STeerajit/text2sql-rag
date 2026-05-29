#!/usr/bin/env python3
"""
Embedding Module
Professional implementation for text embeddings
"""

import os
import requests
import numpy as np
from typing import List, Optional, Union
from sentence_transformers import SentenceTransformer
try:
    from dotenv import load_dotenv
    # Try default
    load_dotenv()
    # Also try project root two levels up
    import pathlib
    project_root_env = pathlib.Path(__file__).resolve().parents[2] / '.env'
    if project_root_env.exists():
        load_dotenv(project_root_env)
except Exception:
    pass

class Embedder:
    """Text embedding handler"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the embedder"""
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        try:
            if self.model_name.startswith("sentence-transformers/"):
                self.model = SentenceTransformer(self.model_name)
            else:
                # For Hugging Face models via API
                self.model = None
        except Exception as e:
            print(f"Warning: Could not initialize embedding model: {e}")
            self.model = None
    
    def embed_texts(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for texts"""
        if isinstance(texts, str):
            texts = [texts]
        
        if self.model is not None:
            # Use local model
            return self.model.encode(texts)
        else:
            # Use Hugging Face API
            return self._embed_via_api(texts)
    
    def _embed_via_api(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings via Hugging Face API"""
        api_key = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HUGGINGFACE_API_TOKEN")
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY/HUGGINGFACE_API_TOKEN not found for API embedding")
        
        pipeline_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}"
        models_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        embeddings = []
        for text in texts:
            try:
                response = requests.post(
                    pipeline_url,
                    headers=headers,
                    json={
                        "inputs": text,
                        "options": {"wait_for_model": True}
                    }
                )
                if response.status_code == 404:
                    # Fallback to /models endpoint
                    response = requests.post(
                        models_url,
                        headers=headers,
                        json={
                            "inputs": text,
                            "options": {"wait_for_model": True}
                        }
                    )
                response.raise_for_status()
                data = response.json()
                # The API can return:
                # - list[dim] for pooled embedding
                # - list[num_tokens][dim] for token embeddings → pool to mean
                # Normalize to unit vector
                vec = self._postprocess_api_embedding(data)
                embeddings.append(vec)
            except Exception as e:
                print(f"Error getting embedding for text: {e}")
                # Return zero vector as fallback
                embeddings.append(np.zeros(384, dtype=np.float32))  # Default dimension
        
        return np.vstack(embeddings)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts"""
        embeddings = self.embed_texts([text1, text2])
        if len(embeddings) == 2:
            # Cosine similarity
            dot_product = np.dot(embeddings[0], embeddings[1])
            norm1 = np.linalg.norm(embeddings[0])
            norm2 = np.linalg.norm(embeddings[1])
            if norm1 > 0 and norm2 > 0:
                return dot_product / (norm1 * norm2)
        return 0.0
    
    def find_most_similar(self, query: str, candidates: List[str], top_k: int = 5) -> List[tuple]:
        """Find most similar texts to query"""
        if not candidates:
            return []
        
        query_embedding = self.embed_texts([query])[0]
        candidate_embeddings = self.embed_texts(candidates)
        
        similarities = []
        for i, candidate_embedding in enumerate(candidate_embeddings):
            similarity = np.dot(query_embedding, candidate_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(candidate_embedding)
            )
            similarities.append((similarity, candidates[i]))
        
        # Sort by similarity and return top_k
        similarities.sort(reverse=True, key=lambda x: x[0])
        return similarities[:top_k]

    def _postprocess_api_embedding(self, data) -> np.ndarray:
        """Post-process HF API embedding output to a 1D normalized vector."""
        # Convert arbitrary nesting to numpy array and pool to 1D
        arr = np.array(data, dtype=np.float32)
        if arr.ndim == 1:
            vec = arr
        elif arr.ndim == 2:
            # tokens x dim → mean over tokens
            vec = arr.mean(axis=0)
        elif arr.ndim == 3:
            # batch x tokens x dim → take batch 0 then mean over tokens
            vec = arr[0].mean(axis=0)
        else:
            vec = arr.reshape(-1).astype(np.float32)
        # Normalize to unit length
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
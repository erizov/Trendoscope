"""
Vector database for semantic search and RAG.
Supports Qdrant and FAISS.
"""
import os
import hashlib
from typing import List, Dict, Any, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    import faiss
except ImportError:
    faiss = None

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    QdrantClient = None


class VectorStore:
    """Abstract vector store interface."""

    def add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> None:
        """Add documents to store."""
        raise NotImplementedError

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        raise NotImplementedError


class FAISSStore(VectorStore):
    """FAISS-based vector store with persistence."""

    def __init__(
        self,
        model_name: str = 'all-MiniLM-L6-v2',
        index_path: str = 'data/faiss_index.bin',
        docs_path: str = 'data/faiss_docs.json'
    ):
        """
        Initialize FAISS store.

        Args:
            model_name: Name of sentence transformer model
            index_path: Path to save/load FAISS index
            docs_path: Path to save/load documents
        """
        if not SentenceTransformer:
            raise ImportError("sentence-transformers not installed")
        if not faiss:
            raise ImportError("faiss not installed")

        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index_path = index_path
        self.docs_path = docs_path

        # Try to load existing index
        if self._load_from_disk():
            pass  # Successfully loaded
        else:
            # Create new index
            self.index = faiss.IndexFlatIP(self.dimension)
            self.documents = []

    def _load_from_disk(self) -> bool:
        """
        Load index and documents from disk.

        Returns:
            True if loaded successfully
        """
        import os
        import json

        if not os.path.exists(self.index_path) or not os.path.exists(self.docs_path):
            return False

        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)

            # Load documents
            with open(self.docs_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)

            return True
        except Exception:
            return False

    def _save_to_disk(self) -> None:
        """Save index and documents to disk."""
        import os
        import json

        # Create directory if needed
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, self.index_path)

        # Save documents
        with open(self.docs_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False)

    def add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> None:
        """
        Add documents to FAISS index and save.

        Args:
            documents: List of documents with 'text' field
        """
        texts = [doc.get('text_plain', doc.get('text', ''))
                for doc in documents]

        if not texts:
            return

        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        # Add to index
        self.index.add(np.array(embeddings).astype('float32'))

        # Store documents
        self.documents.extend(documents)

        # Save to disk
        self._save_to_disk()

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of documents with similarity scores
        """
        if self.index.ntotal == 0:
            return []

        # Generate query embedding
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False
        )

        # Search
        scores, indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            min(top_k, self.index.ntotal)
        )

        # Build results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(score)
                results.append(doc)

        return results


class QdrantStore(VectorStore):
    """Qdrant-based vector store."""

    def __init__(
        self,
        collection_name: str = "trendascope",
        model_name: str = 'all-MiniLM-L6-v2',
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Qdrant store.

        Args:
            collection_name: Name of Qdrant collection
            model_name: Name of sentence transformer model
            url: Qdrant URL
            api_key: Qdrant API key
        """
        if not SentenceTransformer:
            raise ImportError("sentence-transformers not installed")
        if not QdrantClient:
            raise ImportError("qdrant-client not installed")

        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

        url = url or os.getenv("QDRANT_URL", ":memory:")
        api_key = api_key or os.getenv("QDRANT_API_KEY")

        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name

        # Create collection if not exists
        try:
            self.client.get_collection(collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.dimension,
                    distance=Distance.COSINE
                )
            )

    def add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> None:
        """
        Add documents to Qdrant.

        Args:
            documents: List of documents with 'text' field
        """
        if not documents:
            return

        texts = [doc.get('text_plain', doc.get('text', ''))
                for doc in documents]

        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        # Create points
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Generate unique ID
            doc_id = hashlib.md5(
                str(doc).encode('utf-8')
            ).hexdigest()[:16]

            point = PointStruct(
                id=doc_id,
                vector=embedding.tolist(),
                payload=doc
            )
            points.append(point)

        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of documents with similarity scores
        """
        # Generate query embedding
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False
        )[0]

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k
        )

        # Build output
        output = []
        for result in results:
            doc = result.payload.copy()
            doc['score'] = result.score
            output.append(doc)

        return output


# Global store instance
_store = None


def get_store(backend: str = "faiss") -> VectorStore:
    """
    Get or create global vector store.

    Args:
        backend: Backend type (faiss or qdrant)

    Returns:
        Vector store instance
    """
    global _store
    if _store is None:
        if backend == "qdrant":
            _store = QdrantStore()
        else:
            _store = FAISSStore()
    return _store


def index_documents(documents: List[Dict[str, Any]]) -> None:
    """Index documents in vector store."""
    store = get_store()
    store.add_documents(documents)


def search_similar(
    query: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """Search for similar documents."""
    store = get_store()
    return store.search(query, top_k)


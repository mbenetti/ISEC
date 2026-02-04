# Semantic Distance Calculator using Ollama Embeddings and Chroma
# Measures semantic similarity between sentences using embeddings

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import chromadb
import numpy as np
import pandas as pd
from chromadb.config import Settings
from ollama import Client as OllamaClient

from config import Config


@dataclass
class SemanticDistanceResult:
    """Complete result of semantic distance calculation between two sentences."""

    str1: str
    str2: str
    embedding1: List[float]
    embedding2: List[float]
    cosine_distance: float  # 1 - cosine_similarity (0=identical, 1=orthogonal)
    cosine_similarity: float  # Range from -1 to 1
    metadata1: Dict = field(default_factory=dict)
    metadata2: Dict = field(default_factory=dict)

    @property
    def normalized_distance(self) -> float:
        """Normalized distance (0 to 1 scale). 0=identical, 1=opposite."""
        return (1 - self.cosine_similarity) / 2

    @property
    def similarity_percentage(self) -> float:
        """Similarity as percentage (0-100)."""
        return max(0, (self.cosine_similarity + 1) / 2 * 100)

    @property
    def distance_percentage(self) -> float:
        """Distance as percentage (0-100)."""
        return 100 - self.similarity_percentage


class SemanticDistanceCalculator:
    """
    Semantic distance calculator using Ollama embeddings and Chroma vector database.

    Features:
    - Generate embeddings using local Ollama model
    - Store embeddings in Chroma vector database
    - Calculate semantic distances between all sentence pairs
    - Support metadata (frequency, group, etc.)
    - Detailed similarity and distance metrics
    """

    def __init__(
        self,
        ollama_host: str = None,
        embedding_model: str = None,
        collection_name: str = "sentences",
    ):
        """
        Initialize the semantic distance calculator.

        Args:
            ollama_host: URL for Ollama service (uses Config if None)
            embedding_model: Embedding model to use (uses Config if None)
            collection_name: Name for Chroma collection
        """
        self.ollama_host = ollama_host or Config.OLLAMA_HOST
        self.embedding_model = embedding_model or Config.OLLAMA_EMBEDDING_MODEL
        self.collection_name = collection_name

        # Initialize Ollama client
        self.ollama_client = OllamaClient(host=ollama_host)

        # Initialize Chroma client with in-memory storage
        self.chroma_client = chromadb.Client()

        # Collection to store embeddings
        self.collection = None

        # Store embeddings in memory for comparison
        self.embeddings_cache: Dict[str, List[float]] = {}
        self.metadata_cache: Dict[str, Dict] = {}

        print(f"Initialized SemanticDistanceCalculator")
        print(f"  Ollama Host: {ollama_host}")
        print(f"  Embedding Model: {embedding_model}")
        print(f"  Collection: {collection_name}")

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text using Ollama.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]

        try:
            response = self.ollama_client.embed(model=self.embedding_model, input=text)
            embedding = response["embeddings"][0]
            self.embeddings_cache[text] = embedding
            return embedding
        except Exception as e:
            print(f"Error getting embedding for '{text}': {e}")
            raise

    def load_sentences(
        self, sentences: List[str], metadata_list: Optional[List[Dict]] = None
    ) -> None:
        """
        Load sentences and generate embeddings.

        Args:
            sentences: List of sentences to embed
            metadata_list: List of metadata dictionaries (one per sentence)
        """
        if metadata_list is None:
            metadata_list = [{} for _ in sentences]

        if len(sentences) != len(metadata_list):
            raise ValueError("Number of sentences and metadata must match")

        print(f"\nGenerating embeddings for {len(sentences)} sentences...")

        # Create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )

        # Generate embeddings and store
        embeddings = []
        ids = []

        for i, (sentence, metadata) in enumerate(zip(sentences, metadata_list)):
            try:
                embedding = self.get_embedding(sentence)
                embeddings.append(embedding)
                ids.append(f"sent_{i}_{sentence[:10]}") # unique ids based somewhat on content
                self.metadata_cache[sentence] = metadata
                print(
                    f"  ✓ Embedded sentence {i + 1}/{len(sentences)}: {sentence[:50]}..."
                )
            except Exception as e:
                print(f"  ✗ Failed to embed sentence {i + 1}: {e}")
                continue

        # Add to Chroma collection
        if embeddings:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadata_list,
                documents=sentences,
            )
            print(f"\nLoaded {len(embeddings)} embeddings into Chroma collection")
        else:
            print("Failed to generate any embeddings")

    def calculate_semantic_distance(
        self, str1: str, str2: str
    ) -> SemanticDistanceResult:
        """
        Calculate semantic distance between two sentences using Chroma similarity search.

        Args:
            str1: First sentence
            str2: Second sentence

        Returns:
            SemanticDistanceResult with distance metrics
        """
        # Get embeddings
        embedding1 = self.get_embedding(str1)
        embedding2 = self.get_embedding(str2)

        # Query Chroma to find similarity (it uses cosine distance by default with hnsw:space cosine)
        # We search for str2's embedding in the collection and find str1
        results = self.collection.query(
            query_embeddings=[embedding1],
            n_results=len(self.collection.get()["ids"]),  # Get all results
            include=["distances", "embeddings", "metadatas", "documents"],
        )

        # Find the distance to str2
        cosine_distance = None
        cosine_similarity = None

        if results and results["documents"] and len(results["documents"]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                if doc == str2:
                    # Chroma returns distances (not similarities)
                    # For cosine with normalized vectors: distance = 1 - similarity
                    cosine_distance = results["distances"][0][i]
                    cosine_similarity = 1 - cosine_distance
                    break

        # If not found in query results, manually calculate
        if cosine_distance is None:
            # Manual calculation: normalize embeddings and compute cosine similarity
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)

            # Normalize
            emb1_norm = emb1 / (np.linalg.norm(emb1) + 1e-8)
            emb2_norm = emb2 / (np.linalg.norm(emb2) + 1e-8)

            # Cosine similarity
            cosine_similarity = np.dot(emb1_norm, emb2_norm)
            cosine_distance = 1 - cosine_similarity

        # Get metadata
        metadata1 = self.metadata_cache.get(str1, {})
        metadata2 = self.metadata_cache.get(str2, {})

        return SemanticDistanceResult(
            str1=str1,
            str2=str2,
            embedding1=embedding1,
            embedding2=embedding2,
            cosine_distance=cosine_distance,
            cosine_similarity=cosine_similarity,
            metadata1=metadata1,
            metadata2=metadata2,
        )

    def calculate_all_distances(
        self, sentences: List[str]
    ) -> List[SemanticDistanceResult]:
        """
        Calculate semantic distances between all pairs of sentences.

        Args:
            sentences: List of sentences

        Returns:
            List of SemanticDistanceResult for all pairs
        """
        results = []

        total_pairs = len(sentences) * (len(sentences) - 1) // 2
        pair_count = 0

        print(f"\nCalculating semantic distances for {total_pairs} pairs...")

        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                sent1 = sentences[i]
                sent2 = sentences[j]
                result = self.calculate_semantic_distance(sent1, sent2)
                results.append(result)
                pair_count += 1
                if pair_count % 10 == 0:
                    print(f"  Processed {pair_count}/{total_pairs} pairs...", end="\r")

        print(f"  Processed {total_pairs}/{total_pairs} pairs. Done.")
        return results

    def find_top_k_semantic_matches(
        self,
        query_sentence: str,
        k: int = 3,
        exclude_same_group: bool = False,
        exclude_same_subgroup: bool = False,
        source_filter: str = None,
    ) -> List[Tuple[str, float, Dict]]:
        """
        Find top k closest sentences by semantic distance.

        Args:
            query_sentence: Sentence to find matches for
            k: Number of matches
            exclude_same_group: Exclude matches from same group
            exclude_same_subgroup: Exclude matches from same subgroup
            source_filter: Optional source string to filter results

        Returns:
            List of (sentence, normalized_distance, metadata)
        """
        embedding = self.get_embedding(query_sentence)
        
        # Build where clause
        where_clause = {}
        if source_filter:
            where_clause["source"] = source_filter

        # Helper to get current metadata for query sentence if it exists in our cache
        current_metadata = self.metadata_cache.get(query_sentence, {})
        current_group = current_metadata.get("group")
        current_subgroup = current_metadata.get("subgroup")

        # Fetch candidate matches
        # We fetch more than k because we might filter some out
        fetch_k = k * 10 # heuristic: fetch 10x to be safe
            
        # Limit to collection size
        collection_count = self.collection.count()
        if fetch_k > collection_count:
            fetch_k = collection_count
        
        # Avoid 0
        if fetch_k < 1:
            fetch_k = 1

        query_args = {
            "query_embeddings": [embedding],
            "n_results": fetch_k,
            "include": ["distances", "metadatas", "documents"],
        }
        
        if where_clause:
            query_args["where"] = where_clause

        try:
            results = self.collection.query(**query_args)
        except Exception as e:
            # Fallback if query fails (e.g. invalid where clause or empty collection)
            print(f"Query error: {e}")
            return []
        
        potential_matches = []
        
        if results and results["documents"] and len(results["documents"]) > 0:
            docs = results["documents"][0]
            dists = results["distances"][0]
            metas = results["metadatas"][0]
            
            for doc, dist, meta in zip(docs, dists, metas):
                if doc == query_sentence:
                    continue
                
                # Double check source if we can (Chroma should have filtered, but safer)
                if source_filter and meta.get("source") != source_filter:
                    continue
                    
                # Filter by group/subgroup
                if exclude_same_group and current_group is not None:
                    if meta.get("group") == current_group:
                        continue
                        
                if exclude_same_subgroup and current_subgroup is not None:
                    if meta.get("subgroup") == current_subgroup:
                        continue
                
                # Convert cosine distance to normalized distance (0-1)
                cosine_similarity = 1 - dist
                normalized_distance = (1 - cosine_similarity) / 2
                
                potential_matches.append((doc, normalized_distance, meta))
                
        # Sort by distance and take top k
        potential_matches.sort(key=lambda x: x[1])
        return potential_matches[:k]


def load_sentences_from_excel(
    file_path: str,
    name_column: str = "Name",
    frequency_column: str = "Frequency",
    group_column: Optional[str] = None,
    subgroup_column: Optional[str] = None,
) -> Tuple[List[str], List[Dict]]:
    """
    Load sentences and metadata from an Excel file, ensuring all sentences are unique.
    Duplicate sentences are merged by summing frequencies and keeping the highest group/subgroup values.

    Args:
        file_path: Path to the Excel file
        name_column: Name of the column containing sentences
        frequency_column: Name of the column containing frequencies
        group_column: Optional name of the column containing group labels
        subgroup_column: Optional name of the column containing subgroup labels

    Returns:
        Tuple of (sentences_list, metadata_list) where metadata_list contains dictionaries with frequency, group, subgroup
    """
    try:
        df = pd.read_excel(file_path)

        # Group by sentence (name_column) and merge duplicates
        if name_column in df.columns:
            # Group by the sentence column
            grouped = df.groupby(name_column)

            # Lists to store unique sentences and their merged metadata
            unique_sentences = []
            merged_metadata_list = []

            # Process each group of duplicate sentences
            for sentence, group in grouped:
                unique_sentences.append(sentence)

                # Merge metadata for this sentence
                merged_metadata = {}

                # Sum frequencies if frequency column exists
                if frequency_column in group.columns:
                    merged_metadata["frequency"] = int(group[frequency_column].sum())
                else:
                    merged_metadata["frequency"] = 1

                # Keep the first group value if group column exists
                if group_column and group_column in group.columns:
                    # Get non-null group values and keep the first one
                    non_null_groups = group[group_column].dropna()
                    if len(non_null_groups) > 0:
                        merged_metadata["group"] = str(non_null_groups.iloc[0])

                # Keep the first subgroup value if subgroup column exists
                if subgroup_column and subgroup_column in group.columns:
                    # Get non-null subgroup values and keep the first one
                    non_null_subgroups = group[subgroup_column].dropna()
                    if len(non_null_subgroups) > 0:
                        merged_metadata["subgroup"] = str(non_null_subgroups.iloc[0])

                merged_metadata_list.append(merged_metadata)

            return unique_sentences, merged_metadata_list
        else:
            # Fallback to original behavior if name_column doesn't exist
            sentences = df[name_column].tolist()

            # Build metadata for each sentence
            metadata_list = []
            for idx, row in df.iterrows():
                metadata = {}
                if frequency_column in df.columns:
                    metadata["frequency"] = int(row[frequency_column])
                if group_column and group_column in df.columns:
                    metadata["group"] = str(row[group_column])
                if subgroup_column and subgroup_column in df.columns:
                    metadata["subgroup"] = str(row[subgroup_column])
                metadata_list.append(metadata)

            return sentences, metadata_list

    except FileNotFoundError:
        print(f"Error: Excel file '{file_path}' not found")
        raise
    except Exception as e:
        print(f"Error loading sentences from Excel: {e}")
        raise

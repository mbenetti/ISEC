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
                ids.append(f"sent_{i}")
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

        for i, sent1 in enumerate(sentences):
            for sent2 in sentences[i + 1 :]:
                try:
                    result = self.calculate_semantic_distance(sent1, sent2)
                    results.append(result)
                    pair_count += 1
                    print(f"Calculated pair {pair_count}/{total_pairs}")
                except Exception as e:
                    print(
                        f"Error calculating distance between '{sent1}' and '{sent2}': {e}"
                    )
                    continue

        return results

    def find_closest_sentence(
        self,
        query_sentence: str,
        exclude_same_group: bool = False,
        exclude_same_subgroup: bool = False,
    ) -> Optional[SemanticDistanceResult]:
        """
        Find the closest semantic sentence in the collection to the query sentence (excluding itself).

        Args:
            query_sentence: The sentence to find matches for
            exclude_same_group: If True, exclude sentences from the same group
            exclude_same_subgroup: If True, exclude sentences from the same subgroup

        Returns:
            SemanticDistanceResult with the closest sentence, or None if not found
        """
        if not self.collection:
            print("Error: Collection not loaded. Call load_sentences() first.")
            return None

        try:
            # Get embedding for query sentence
            query_embedding = self.get_embedding(query_sentence)

            # Get query sentence metadata to determine group/subgroup for exclusion
            query_metadata = self.metadata_cache.get(query_sentence, {})
            query_group = query_metadata.get("group") if exclude_same_group else None
            query_subgroup = (
                query_metadata.get("subgroup") if exclude_same_subgroup else None
            )

            # Build where clause for Chroma filtering
            where_clause = {}
            if query_group is not None:
                where_clause["group"] = {"$ne": query_group}
            if query_subgroup is not None:
                where_clause["subgroup"] = {"$ne": query_subgroup}

            # Query Chroma to find closest matches
            # Request more results to ensure we can exclude the query sentence itself and filtered results
            all_docs = self.collection.get()["documents"]
            n_results = min(
                len(all_docs), 20
            )  # Get up to 20 results to account for filtering

            # Apply filtering if needed
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "include": ["distances", "embeddings", "metadatas", "documents"],
            }

            if where_clause:
                query_params["where"] = where_clause

            results = self.collection.query(**query_params)

            if (
                not results
                or not results["documents"]
                or len(results["documents"][0]) == 0
            ):
                print(f"No results found for: {query_sentence}")
                return None

            # Find the closest match that is NOT the query sentence itself
            closest_idx = None
            for i, doc in enumerate(results["documents"][0]):
                if doc != query_sentence:
                    closest_idx = i
                    break

            if closest_idx is None:
                print(f"No other matches found besides the query sentence itself")
                return None

            closest_sentence = results["documents"][0][closest_idx]
            closest_distance = results["distances"][0][closest_idx]
            closest_similarity = 1 - closest_distance

            # Get metadata for closest sentence
            closest_metadata = self.metadata_cache.get(closest_sentence, {})

            return SemanticDistanceResult(
                str1=query_sentence,
                str2=closest_sentence,
                embedding1=query_embedding,
                embedding2=results["embeddings"][0][closest_idx]
                if results["embeddings"]
                else [],
                cosine_distance=closest_distance,
                cosine_similarity=closest_similarity,
                metadata1=query_metadata,
                metadata2=closest_metadata,
            )

        except Exception as e:
            print(f"Error finding closest sentence for '{query_sentence}': {e}")
            return None

    def find_top_k_semantic_matches(
        self,
        query_sentence: str,
        k: int = 3,
        exclude_same_group: bool = False,
        exclude_same_subgroup: bool = False,
    ) -> List[Tuple[str, float, Dict]]:
        """
        Find top k closest sentences by semantic distance with optional group/subgroup exclusion.

        Args:
            query_sentence: The sentence to find matches for
            k: Number of top matches to retrieve
            exclude_same_group: If True, exclude sentences from the same group
            exclude_same_subgroup: If True, exclude sentences from the same subgroup

        Returns:
            List of (sentence, normalized_distance, metadata) tuples sorted by distance (ascending)
        """
        if not self.collection:
            print("Error: Collection not loaded. Call load_sentences() first.")
            return []

        try:
            # Get embedding for query sentence
            query_embedding = self.get_embedding(query_sentence)

            # Get query sentence metadata to determine group/subgroup for exclusion
            query_metadata = self.metadata_cache.get(query_sentence, {})
            query_group = query_metadata.get("group") if exclude_same_group else None
            query_subgroup = (
                query_metadata.get("subgroup") if exclude_same_subgroup else None
            )

            # Build where clause for Chroma filtering
            where_clause = {}
            if query_group is not None:
                where_clause["group"] = {"$ne": query_group}
            if query_subgroup is not None:
                where_clause["subgroup"] = {"$ne": query_subgroup}

            # Query Chroma to find top k matches
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": k + 10,  # Get extra results to account for filtering
                "include": ["distances", "documents"],
            }

            if where_clause:
                query_params["where"] = where_clause

            results = self.collection.query(**query_params)

            if (
                not results
                or not results["documents"]
                or len(results["documents"][0]) == 0
            ):
                print(f"No results found for: {query_sentence}")
                return []

            # Collect matches, excluding the query sentence itself
            matches = []
            for doc, distance in zip(results["documents"][0], results["distances"][0]):
                if doc != query_sentence:
                    # Get metadata for this document
                    doc_metadata = self.metadata_cache.get(doc, {})
                    # Normalize distance to 0-1 scale (cosine distance)
                    normalized_distance = distance / 2.0  # Cosine distance ranges 0-2
                    matches.append((doc, normalized_distance, doc_metadata))
                    if len(matches) == k:
                        break

            return matches

        except Exception as e:
            print(f"Error finding top k semantic matches for '{query_sentence}': {e}")
            return []

    def find_closest_for_all(
        self,
        sentences: List[str],
        exclude_same_group: bool = False,
        exclude_same_subgroup: bool = False,
    ) -> List[SemanticDistanceResult]:
        """
        Find the closest sentence for each sentence in the list.

        Args:
            sentences: List of sentences to find closest matches for
            exclude_same_group: If True, exclude sentences from the same group
            exclude_same_subgroup: If True, exclude sentences from the same subgroup

        Returns:
            List of SemanticDistanceResult with closest match for each sentence
        """
        results = []

        for i, sentence in enumerate(sentences):
            print(
                f"Finding closest match for sentence {i + 1}/{len(sentences)}: {sentence[:50]}..."
            )
            result = self.find_closest_sentence(
                sentence, exclude_same_group, exclude_same_subgroup
            )
            if result:
                results.append(result)

        return results

    def print_result(
        self, result: SemanticDistanceResult, show_embeddings: bool = False
    ) -> None:
        """
        Print a formatted semantic distance result.

        Args:
            result: SemanticDistanceResult to print
            show_embeddings: If True, show full embedding vectors
        """
        print(f"\n'{result.str1}' ↔ '{result.str2}'")
        print("-" * 80)
        print(f"  Cosine Similarity: {result.cosine_similarity:.4f}")
        print(f"  Similarity Percentage: {result.similarity_percentage:.2f}%")
        print(f"  Cosine Distance: {result.cosine_distance:.4f}")
        print(f"  Normalized Distance (0-1): {result.normalized_distance:.4f}")
        print(f"  Distance Percentage: {result.distance_percentage:.2f}%")

        if result.metadata1:
            print(f"  Metadata (Sentence 1): {result.metadata1}")
        if result.metadata2:
            print(f"  Metadata (Sentence 2): {result.metadata2}")

        if show_embeddings:
            print(f"  Embedding 1 (first 5): {result.embedding1[:5]}")
            print(f"  Embedding 2 (first 5): {result.embedding2[:5]}")

    def print_batch_results(
        self, results: List[SemanticDistanceResult], show_embeddings: bool = False
    ) -> None:
        """
        Print formatted results for multiple sentence pairs.

        Args:
            results: List of SemanticDistanceResult objects
            show_embeddings: If True, show embedding vectors
        """
        print("\n" + "=" * 80)
        print("Semantic Distance Results for All Pairs")
        print("=" * 80)

        for result in results:
            self.print_result(result, show_embeddings=show_embeddings)


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
        Tuple of (sentences_list, metadata_list)
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


def main():
    """Main function demonstrating semantic distance calculation."""

    print("=" * 80)
    print("Semantic Distance Calculator with Ollama Embeddings")
    print("=" * 80)

    # Load sentences from Excel
    try:
        sentences, metadata_list = load_sentences_from_excel(
            Config.SENTENCES_FILE,
            name_column=Config.SENTENCES_NAME_COLUMN,
            frequency_column=Config.SENTENCES_FREQUENCY_COLUMN,
            group_column=Config.SENTENCES_GROUP_COLUMN,
            subgroup_column=Config.SENTENCES_SUBGROUP_COLUMN,
        )
        print(f"\nLoaded {len(sentences)} sentences from {Config.SENTENCES_FILE}")
    except FileNotFoundError:
        print(f"Using default example sentences")
        sentences = ["XDKT11T3", "XDKG11T3", "LDKT11T3"]
        metadata_list = [{"frequency": 1} for _ in sentences]

    print(f"Sentences: {sentences}\n")

    # Create calculator
    calculator = SemanticDistanceCalculator(
        ollama_host=Config.OLLAMA_HOST, embedding_model=Config.OLLAMA_EMBEDDING_MODEL
    )

    # Load sentences and generate embeddings
    try:
        calculator.load_sentences(sentences, metadata_list)
    except Exception as e:
        print(f"Error loading sentences: {e}")
        print("Make sure Ollama is running with the embeddinggemma model:")
        print("  ollama run embeddinggemma")
        return

    # Calculate distances between all pairs
    print("\n" + "=" * 80)
    print("Calculating semantic distances...")
    print("=" * 80)
    import time
    start_time = time.time()
    results = calculator.calculate_all_distances(sentences)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nProcessing complete in {elapsed_time:.2f} seconds.")
    print(f"Processed {len(sentences)} items.")

    # Print results
    calculator.print_batch_results(results)

    # Find and display closest sentence for each sentence
    print("\n" + "=" * 80)
    print("Closest Semantic Match for Each Sentence (No Filtering)")
    print("=" * 80)

    closest_results = calculator.find_closest_for_all(sentences)

    print("\n" + "=" * 80)
    print("Closest Matches Analysis (No Filtering)")
    print("=" * 80)

    for result in closest_results:
        calculator.print_result(result)

    # Demonstrate filtering functionality if metadata contains group information
    has_group_data = any("group" in metadata for metadata in metadata_list)
    if has_group_data:
        print("\n" + "=" * 80)
        print("Closest Semantic Match for Each Sentence (Excluding Same Group)")
        print("=" * 80)

        closest_results_filtered = calculator.find_closest_for_all(
            sentences, exclude_same_group=True
        )

        print("\n" + "=" * 80)
        print("Closest Matches Analysis (Excluding Same Group)")
        print("=" * 80)

        for result in closest_results_filtered:
            calculator.print_result(result)
            # Show group information
            group1 = result.metadata1.get("group", "N/A")
            group2 = result.metadata2.get("group", "N/A")
            print(f"  Groups: {group1} -> {group2}")


if __name__ == "__main__":
    main()

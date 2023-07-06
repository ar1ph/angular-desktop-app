
import sys, os
from typing import Any
from .base import BaseVectorstore
from tqdm import tqdm
from uuid import uuid1
from chromadb import Client
from chromadb.config import Settings
from chromadb.api.types import QueryResult 
sys.path.append('..')
from embeddings.base import BaseEmbedding
from embeddings.HuggingFaceEmbedding import HuggingFaceEmbedding


class Chroma(BaseVectorstore):
    """
    A class representing the Chroma vector store for document search.

    Attributes:
        SEARCH_STRATEGIES (set): Supported search strategies for Chroma.
        name (str): Name of the vector store (Chroma).
        emb_model_name (str): Name of the embedding model.
        persist_directory (str): Directory for persisting the Chroma database.
        _client (Client): Chroma client instance.
        _collection (Collection): Chroma collection instance.

    Methods:
        __init__: Initialize the Chroma vector store.
        _collection_exist: Check if a collection exists in the Chroma database.
        __setattr__: Set attribute value with additional validation.
        _add_collection: Add a new collection to the Chroma database.
        add_data: Add data to the Chroma collection.
        query: Execute a query on the Chroma collection.
        get_available_strategies: Get the available search strategies for Chroma.
        get_max_n: Get the maximum number of results in the Chroma collection.
        __call__: Not implemented.
    """

    SEARCH_STRATEGIES = {'ip', 
                         'cosine', 
                         'l2'}

    def __init__(self, 
                 embedding: BaseEmbedding, 
                 strategy: str
                 ) -> None:
        """
        Initialize the Chroma vector store.

        Args:
            embedding (BaseEmbedding): The embedding model to use.
            strategy (str): The search strategy to use.
        """
        _DATABASE_DIRECTORY = os.path.join(os.path.abspath(os.pardir), "database")
        super().__init__(embedding=embedding, strategy=strategy)
        self.name = 'Chroma'
        emb_model_name = embedding.get_name()
        self.emb_model_name = emb_model_name
        self.persist_directory = os.path.join(_DATABASE_DIRECTORY, f"{emb_model_name}__Chroma")
        self._client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=self.persist_directory))
        self._add_collection()

    def _collection_exist(self, 
                          name: str
                          ) -> bool:
        """
        Check if a collection exists in the Chroma database.

        Args:
            name (str): The name of the collection.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        try:
            collection = self._client.get_collection(name)
            return True
        except:
            return False

    def __setattr__(self, 
                    __name: str, 
                    __value: Any
                    ) -> None:
        """
        Set attribute value with additional validation.

        Args:
            __name (str): The name of the attribute.
            __value (Any): The value to be set.

        Raises:
            ValueError: If the embedding is not of type BaseEmbedding.
            ValueError: If the strategy is not supported.
        """
        if __name == "embedding":
            if not isinstance(__value, BaseEmbedding):
                error_msg = "Embedding must be of BaseEmbedding type"
                raise ValueError(error_msg)
        elif __name == "strategy":
            if __value not in Chroma.SEARCH_STRATEGIES:
                error_msg = f"{__value} search strategy is not supported"
                raise ValueError(error_msg)

        return super().__setattr__(__name, __value)

    def _add_collection(self) -> None:
        """
        Add a new collection to the Chroma database.
        """
        name = 'chroma_collection'
        metadata = {'hnsw:space': self.strategy, 'hnsw:construction_ef': 4096, 'hnsw:search_ef': 4096, 'hnsw:M': 100}
        func = self.embedding.get_function()
        if self._collection_exist(name):
            self._client.reset()
        kwargs = {"name": name, "metadata": metadata, "embedding_function": func}
        self._collection = self._client.create_collection(**kwargs)

    def add_data(self, 
                 data_directory: str
                 ) -> None:
        """
        Add data to the Chroma collection.

        Args:
            data_directory (str): The directory containing the data files.
        """
        docs = super().process_documents(data_directory=data_directory)
        with tqdm(total=len(docs), desc="Adding documents", ncols=80) as pbar:
            for doc in docs:
                self._collection.add(ids=[str(uuid1())], metadatas=[doc.metadata], documents=[doc.page_content])
                pbar.update()
        self._client.persist()

    def query(self, 
              query_text: str, 
              n_results: int, 
              include: list[str]
              ) -> QueryResult:
        """
        Execute a query on the Chroma collection.

        Args:
            query_text (str): The query text.
            n_results (int): The number of results to retrieve.
            include (list): The list of fields to include in the results.

        Returns:
            dict: The query result.
        """
        if n_results == -1:
            return self._collection.query(query_texts=query_text, n_results=self.get_max_n(), include=include)
        return self._collection.query(query_texts=query_text, n_results=n_results, include=include)

    def get_available_strategies(self) -> list[str]:
        """
        Get the available search strategies for Chroma.

        Returns:
            list: A list of available search strategies.
        """
        return Chroma.SEARCH_STRATEGIES

    def get_max_n(self) -> int:
        """
        Get the maximum number of results in the Chroma collection.

        Returns:
            int: The maximum number of results.
        """
        return self._collection.count()

    def __call__(self, 
                 embedding: BaseEmbedding, 
                 strategy: str, 
                 data_directory: str
                 ) -> None:
        """
        Not implemented.
        """
        raise NotImplementedError()


def main():
    """
    Main function to demonstrate the usage of the Chroma module.
    """
    embedding = HuggingFaceEmbedding(model_name='all-MiniLM-L6-v2')
    chroma = Chroma(embedding=embedding, strategy='ip')
    data_directory = os.path.join(os.path.abspath(os.curdir), 'data_temp')
    chroma.add_data(data_directory=data_directory)
    print(chroma.query(query_text='Describe the ICD-10 Code A01.2', n_results=-1, include=['distances']))


if __name__ == "__main__":
    main()

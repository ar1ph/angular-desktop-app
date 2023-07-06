import sys
import os
from typing import Any
from .base import BaseVectorstore
from tqdm import tqdm
from uuid import uuid1
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
sys.path.append('..')
from embeddings.base import BaseEmbedding
from embeddings.HuggingFaceEmbedding import HuggingFaceEmbedding



class Milvus(BaseVectorstore):
    """
    A class representing the Milvus vector store for document search.

    Attributes:
        SEARCH_STRATEGIES (set): Supported search strategies for Milvus.
        name (str): Name of the vector store (Milvus).
        emb_model_name (str): Name of the embedding model.
        _collection (Collection): Milvus collection instance.

    Methods:
        __init__: Initialize the Milvus vector store.
        _collection_exist: Check if a collection exists in the Milvus database.
        __setattr__: Set attribute value with additional validation.
        _add_collection: Add a new collection to the Milvus database.
        add_data: Add data to the Milvus collection.
        _process_output: Process the query output.
        query: Execute a query on the Milvus collection.
        get_available_strategies: Get the available search strategies for Milvus.
        get_max_n: Get the maximum number of results in the Milvus collection.
        __call__: Not implemented.
    """

    SEARCH_STRATEGIES = {'ip',
                         'l2'}

    def __init__(self,
                 embedding,
                 strategy,
                 host="localhost",
                 port="19530",
                 ) -> None:
        """
        Initialize the Milvus vector store.

        Args:
            embedding: The embedding model to use.
            strategy: The search strategy to use.
            host: The Milvus server host.
            port: The Milvus server port.
        """
        super().__init__(embedding=embedding,
                         strategy=strategy)
        self.name = 'Milvus'
        emb_model_name = embedding.get_name()
        self.emb_model_name = emb_model_name
        connections.connect("default",
                            host=host,
                            port=port)
        self._add_collection()


    def _collection_exist(self,
                          name : str
                         ) -> bool:
        """
        Check if a collection exists in the Milvus database.

        Args:
            name (str): The name of the collection.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return utility.has_collection(name)


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
            if not __value in Milvus.SEARCH_STRATEGIES:
                error_msg = f"{__value} search strategy is not supported"
                raise ValueError(error_msg)
            
        return super().__setattr__(__name, __value)
    

    def _add_collection(self):
        """
        Add a new collection to the Milvus database.
        """
        name = 'milvus_collection'
        if self._collection_exist(name): 
            utility.drop_collection(name) 
        id_field = FieldSchema(
            name="ids",
            dtype=DataType.VARCHAR,
            is_primary=True, 
            auto_id=False, 
            max_length=64
        )
        metadata_field = FieldSchema(
            name="source",
            dtype=DataType.VARCHAR,
            max_length=512

        )
        embed_field = FieldSchema(
            name="embeddings",
            dtype=DataType.FLOAT_VECTOR,
            dim=self.embedding.get_dimension()
        )
        doc_field = FieldSchema(
            name="documents",
            dtype=DataType.VARCHAR,
            max_length=65535
        )

        fields = [id_field, metadata_field, embed_field,  doc_field]
        schema = CollectionSchema(fields, "Milvus collection")
        self._collection = Collection(name, schema, consistency_level="Strong")
        print(self._collection.description)
        
    

    def add_data(self, 
                 data_directory: str
                 ) -> None:
        """
        Add data to the Milvus collection.

        Args:
            data_directory (str): The directory containing the data files.
        """
        
        docs = super().process_documents(data_directory=data_directory)
        datas = [[], [], [], []]
        with tqdm(total=len(docs), 
                    desc="Extracting datas", 
                    ncols=80) as pbar:
            for doc in docs: 
                datas[0].append(str(uuid1()))
                datas[1].append(doc.metadata['source'])
                datas[2].append(self.embedding.from_text(doc.page_content))
                datas[3].append(doc.page_content)
                pbar.update() 
        self._collection.insert(datas)
        self._collection.flush() 
        field_params = {
            "index_type": "FLAT",
            "metric_type": "IP", 
        }
        self._collection.create_index("embeddings", field_params)
        self._collection.load()

    def _process_output(self,
                        output,
                        include):
        """
        Process the query output.

        Args:
            output: The query output.
            include: The list of fields to include in the results.

        Returns:
            dict: The processed query result.
        """
        all_fields = {
            "ids":[],
            "distances":[],
            "metadatas":[[]],
            "documents":[]
        }
        for row in output[0]:
            row_dict = row.to_dict()
            all_fields['ids'].append(row_dict['id'])
            all_fields['distances'].append(row_dict['distance'])
            all_fields['metadatas'][0].append({'source':row_dict['entity']['source']})
            all_fields['documents'].append(row_dict['entity']['documents'])
        
        new_output = dict()
        for field in include : new_output[field] = all_fields[field] 
        return new_output
        
    def query(self, 
              query_text: str, 
              n_results: int,
              include: list[str]):
        """
        Execute a query on the Milvus collection.

        Args:
            query_text (str): The query text.
            n_results (int): The number of results to retrieve.
            include (list): The list of fields to include in the results.

        Returns:
            dict: The query result.
        """
        query_vector = self.embedding.from_text(query_text)
        limit = self._collection.num_entities if n_results == -1 else n_results
        param = {
            "metric_type": "IP",
            "limit": limit, 
        }
        output = self._collection.search(data=[query_vector],
                                         anns_field="embeddings",
                                         param=param,
                                         output_fields=['source',
                                                        'documents'],
                                         limit=limit) 
        return self._process_output(output=output,
                                    include=include)
        
        
    def get_available_strategies(self) -> list[str]:
        """
        Get the available search strategies for Milvus.

        Returns:
            list: The list of available search strategies.
        """
        return Milvus.SEARCH_STRATEGIES
    
    def get_max_n(self) -> int:
        """
        Get the maximum number of results in the Milvus collection.

        Returns:
            int: The maximum number of results.
        """
        return self._collection.num_entities
    
    def __call__(self, 
                 embedding, 
                 strategy, 
                 data_directory: str
                 ) -> None:
        """
        Not implemented.
        """
        raise NotImplementedError()

    


def main(): 
    embedding = HuggingFaceEmbedding(model_name='all-MiniLM-L6-v2') 
    milvus = Milvus(embedding=embedding, strategy='ip')
    milvus.add_data(os.path.join(os.path.abspath(os.pardir), 'data_temp')) 
    print(milvus.query("Describe the ICD-10 CM Code A01.2", n_results=-1, include=["metadatas"]))


if __name__ == "__main__": main()
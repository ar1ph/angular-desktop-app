import os

from abc import ABC, abstractmethod
from typing import Any
from tqdm import tqdm
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class BaseVectorstore(ABC):

    DOC_LOADER = {'.txt' : lambda file_path : 
                           TextLoader(file_path=file_path,
                                      autodetect_encoding=True).load()}

    def __init__(self,
                 embedding,
                 strategy) -> None:
        self.embedding = embedding
        self.strategy = strategy
        super().__init__()

    @classmethod
    def retrieve_file_paths(cls,
                            data_directory : str) -> list[str]:
        
        file_paths = []

        for root, _, files in os.walk(data_directory):
            # print("Files: ", files)
            with tqdm(total=len(files), 
                      desc="Retrieving file paths", 
                      ncols=80) as pbar:
                for file_name in files:
                    file_paths.append(os.path.join(root, file_name))
                    pbar.update()
        return file_paths
    
    @classmethod
    def _load_document(cls,
                       file_path : str):
        
        file_extension = os.path.splitext(file_path)[1]
        if not file_extension in cls.DOC_LOADER:
            error_msg = f'Unsupport file extension: {file_extension}'
            raise ValueError(error_msg)
        
        return cls.DOC_LOADER[file_extension](file_path=file_path)

    
    @classmethod
    def load_documents(cls,
                       file_paths: list[str]):
        
        if len(file_paths) == 0:
            raise ValueError("Number of filepaths can't be zero")
        docs = cls._load_document(file_paths[0])
        for path in file_paths[1:]: 
            docs.extend(cls._load_document(file_path=path))

        return docs    


    @classmethod
    def process_documents(cls,
                          data_directory : str) :
        
        
        file_paths = cls.retrieve_file_paths(data_directory=data_directory)
        print("Data directory: ", data_directory)
        loaded_docs = cls.load_documents(file_paths=file_paths)
        splitter = RecursiveCharacterTextSplitter(chunk_size=750,
                                                  chunk_overlap=100)
        splitted_docs = splitter.split_documents(loaded_docs)
        
        return splitted_docs
    

    @abstractmethod
    def add_data(self, 
                 data_directory: str) -> None:
        pass

    @abstractmethod
    def query(self,
              query_text: str,
              n_results: int):
        pass

    @abstractmethod
    def get_available_strategies(self) -> list[str]:
        pass

    @abstractmethod
    def get_max_n(self) -> int:
        pass

    @abstractmethod
    def __call__(self, 
                 embedding,
                 strategy,
                 data_directory : str
                 ) -> None:
        pass




class Test(BaseVectorstore):

    def __init__(self,
                 embedding,
                 strategy) -> None:
        super().__init__(embedding=embedding,
                         strategy=strategy)

    def add_data(self, data_directory: str):
        return super().add_data(data_directory)
    
    def query(self, query_text: str, n_results: int):
        return super().query(query_text, n_results)
    
    def get_available_strategies(self):
        return super().get_available_strategies()
    
    def get_max_n(self):
        return super().get_max_n()
    
    def __call__(self, data_directory: str) -> None:
        return super().__call__(data_directory)


def main():

    data_directory = os.path.join(os.path.abspath(os.pardir),
                                  'data_temp')
    test = Test(None, None)
    # print(dir(Test))
    file_paths = test.retrieve_file_paths(data_directory=data_directory)
    # print(file_paths[0])
    print(test.load_documents(file_paths=file_paths))



        

if __name__ == "__main__": main()
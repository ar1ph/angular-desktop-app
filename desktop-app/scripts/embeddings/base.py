

from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer


class BaseEmbedding(ABC):

    def __init__(self) -> None:
        super().__init__()


    @abstractmethod
    def get_function(self):
        pass

    @abstractmethod
    def get_name(self):
        pass


    @abstractmethod
    def from_text(self,
                  text: str) -> list[float]:
        pass

    @abstractmethod
    def from_texts(self,
                   texts : list[str]) -> list[list[float]]:
        pass


    def get_dimension(self):
        pass



class TestEmbedding(BaseEmbedding):

    def __init__(self,
                 model_name: str) -> None:
        super().__init__()
        self.name = model_name
        self.model = SentenceTransformer(model_name)


    def from_text(self, text: str) -> list[float]:
        return self.model.encode(text)
    

    def from_texts(self, texts: list[str]) -> list[list[float]]:
        return list(map(self.from_text,
                        texts))


    def get_name(self):
        return self.name
    
    def get_function(self):
        return self.model.encode
    
    def get_dimension(self):
        return self.model.get_sentence_embedding_dimension()


def main():


    test = TestEmbedding("all-MiniLM-L6-v2")

    # print(test.get_function())
    # print(test.from_text("Hello world"))
    v1 = test.from_text("Hello world")
    v2 = test.from_text("Whaljf falsk . Hello world, . What is the name o fthe l. City, banglades")
    # print(len(v1), len(v2))

    print(test.get_dimension())


if __name__ == "__main__": main()


    
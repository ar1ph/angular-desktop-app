from .base import BaseEmbedding
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class HuggingFaceEmbedding(BaseEmbedding):

    def __init__(self,
                 model_name : str) -> None:
        super().__init__()
        self.name = model_name
        self.model = SentenceTransformer(model_name)

    def from_text(self, text: str) -> list[float]:
        return list(self.model.encode(text))
    

    def from_texts(self, texts: list[str]) -> list[list[float]]:
        
        embeddings = []
        with tqdm(total=len(texts),
                  desc='Finding the embeddings',
                  ncols=80) as pbar:
            for text in texts:
                embeddings.append(self.from_text(text=text))
                                  
        return embeddings


    def get_name(self):
        return self.name
    
    def get_function(self):
        return self.model.encode
    
    def get_dimension(self):
        return self.model.get_sentence_embedding_dimension()
    



def main():

    test = HuggingFaceEmbedding('all-MiniLM-L6-v2')

    # print(test.from_text('Hello World'))
    # print(test.from_texts(['Hello', 'world']))
    # print(test.get_dimension())
    print(test.get_function())



if __name__ == "__main__": main()
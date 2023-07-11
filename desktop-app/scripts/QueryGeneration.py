from langchain import PromptTemplate, LLMChain, HuggingFaceHub
from langchain.llms import OpenAI
from getpass import getpass
import os

API_KEY = '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'
os.environ["HUGGINGFACEHUB_API_TOKEN"] = API_KEY 

template = """
Given the following context. Generate a query that could be asked to an LLM. 
Return only one query and nothing else, should end with a question mark:

{context}

"""

prompt = PromptTemplate.from_template(template)

file = open("../data_temp/A01.2.txt")
context = file.readlines()
file.close()

repo_id = "google/flan-t5-xxl"
llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={"temperature": 0.5, "max_length": 64})
llm_chain = LLMChain(prompt=prompt, llm=llm)

print(llm_chain.run(context))










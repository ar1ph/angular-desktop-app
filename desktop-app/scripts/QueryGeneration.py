from langchain import PromptTemplate, LLMChain, HuggingFaceHub
from langchain.llms import OpenAI
import os
import json
import sys
from dotenv import load_dotenv
import random

load_dotenv()

data = json.loads(sys.argv[1])
path = data['path']
source = data['source']
index = data['index']

file_path = os.path.join(path, source)

#Must create .env files with the following key
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("API_KEY")

models = ["google/flan-t5-xxl", "google/flan-t5-base", "google/flan-t5-small", "google/flan-t5-large", "google/flan-t5-xl", "lmsys/fastchat-t5-3b-v1.0"]

template = """
Given the following context. Generate a query that could be asked to an LLM. 
Return only one query and nothing else, should end with a question mark:

{context}

"""

prompt = PromptTemplate.from_template(template)


file = open(file_path)
context = file.readlines()
file.close()

repo_id = models[random.randint(0, len(models)-1)]
llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={
                     "temperature": 0.5, "max_length": 64})
llm_chain = LLMChain(prompt=prompt, llm=llm)

query = llm_chain.run(context)

print(json.dumps([query, index]))

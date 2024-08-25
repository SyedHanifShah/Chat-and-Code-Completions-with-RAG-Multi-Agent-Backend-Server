# Add your utilities or helper functions to this file.

import os
from dotenv import load_dotenv, find_dotenv
from langchain_together import ChatTogether, Together
from pydantic import BaseModel
from typing import  List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_together import TogetherEmbeddings
from langchain_community.vectorstores import Chroma
                                                                                                                   # the format for that file is (without the comment)                                                                                                                                       #API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService
def load_env():
    _ = load_dotenv(find_dotenv())

def get_secret_key():
    load_env()
    SECRET_KEY = os.getenv("SECRET_KEY")
    return SECRET_KEY


def get_togather_api_key():
    load_env()
    TOGATHER_API_KEY = os.getenv("TOGATHER_API_KEY")
    return TOGATHER_API_KEY

def get_serper_api_key():
    load_env()
    openai_api_key = os.getenv("SERPER_API_KEY")
    return openai_api_key


# break line every 80 characters if line is longer than 80 characters
# don't break in the middle of a word
def pretty_print_result(result):
  parsed_result = []
  for line in result.split('\n'):
      if len(line) > 80:
          words = line.split(' ')
          new_line = ''
          for word in words:
              if len(new_line) + len(word) + 1 > 80:
                  parsed_result.append(new_line)
                  new_line = word
              else:
                  if new_line == '':
                      new_line = word
                  else:
                      new_line += ' ' + word
          parsed_result.append(new_line)
      else:
          parsed_result.append(line)
  return "\n".join(parsed_result)



DEFAULT_SYSTEM_PROMPT = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.
Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. 
Please ensure that your responses are socially unbiased and positive in nature.
If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct.
If you don't know the answer to a question, please don't share false information.\n"""



CODE_ASSISTANT_SYSTEM_PROMPT = """You are an expert programming assistant. Your primary function is to assist users with their code-related inquiries. Always provide accurate and efficient solutions to coding problems while maintaining a helpful and respectful demeanor.
Your responses should:
- Be clear and concise.
- Follow best coding practices.
- Include necessary context for better understanding.
- Focus on providing solutions or suggestions to code-related queries.
- Adapt to various programming languages and frameworks.
- Avoid harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.
- Ensure responses are socially unbiased and positive.
- Explain why a provided solution is preferred or how it works, if needed.
- If a question does not make sense or lacks necessary information, request clarification or state that the question is unclear.
- If you don't know the answer to a question, admit it instead of providing false information.
"""

def get_chat_model(model:str, temprature:float, max_tokens=int):
    api_key = get_togather_api_key()
    return ChatTogether(
        api_key=api_key,
        model=model,
        temperature=temprature,
        max_tokens=max_tokens,
        timeout=None,
        max_retries=2,
)
def get_code_model(model:str, temprature:float, max_tokens=int):
    api_key = get_togather_api_key()
    return Together(
         together_api_key=api_key,
    model=model,
    temperature=temprature,
    max_tokens=max_tokens
)

def get_embedding_model(model:str, temprature:float, max_tokens=int):
    api_key = get_togather_api_key()
    return  TogetherEmbeddings(
    model="togethercomputer/m2-bert-80M-8k-retrieval",
    together_api_key = api_key
)


def get_chat_model(model:str, temprature:float, max_tokens=int):
    api_key = get_togather_api_key()
    return ChatTogether(
        api_key=api_key,
        model=model,
        temperature=temprature,
        max_tokens=max_tokens,
        timeout=None,
        max_retries=2,
)

def text_spliting(text:str):
    text_length = len(text)
    if text_length <= 2000:
        chunk_size = 200
        chunk_overlap = 20
    else:
        chunk_size = int(text_length / 10) 
        chunk_overlap = int(chunk_size / 10)

    spliter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len)
    return spliter.split_text(text)


class Message(BaseModel):
    role: str
    content: str

class RequestBody(BaseModel):
    model: str = "meta-llama/Llama-3-70b-chat-hf"
    messages: List[Message]
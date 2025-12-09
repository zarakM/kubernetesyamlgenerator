
from langchain_openai import ChatOpenAI
import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']
chat = ChatOpenAI(temperature=0.0, model=llm_model)


def get_completion(prompt, model=llm_model):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, 
    )
    return response.choices[0].message["content"]

get_completion("What is 1+1?")

# template_string = """Translate the text \
# that is delimited by triple backticks \
# into a style that is {style}. \
# text: ```{text}```
# """

# prompt_template = ChatPromptTemplate.from_template(template_string)

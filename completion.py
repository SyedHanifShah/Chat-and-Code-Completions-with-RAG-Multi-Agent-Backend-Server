
from utils import RequestBody, Message
from utils import DEFAULT_SYSTEM_PROMPT, CODE_ASSISTANT_SYSTEM_PROMPT  ,get_togather_api_key, get_chat_model, get_code_model
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.messages.utils import convert_to_messages



togather_api_ket = get_togather_api_key()





def completion_model(request_body:RequestBody):
    model = request_body.model
    llm = get_chat_model(model=model, temprature=0, max_tokens=1000)
    messages= request_body.messages
    if messages:
        first_message = messages[0]
        if first_message.role != "system":
            messages.insert(0, Message(role="system", content=DEFAULT_SYSTEM_PROMPT))
        first_message = messages.pop(0)
    
        prompt= ChatPromptTemplate.from_messages([
           (first_message.role, first_message.content),
           MessagesPlaceholder(variable_name='messages')
            ])
        formatted_messages = [(msg.role, msg.content) for msg in messages]
        converted_messages = convert_to_messages(formatted_messages)
        chain = prompt | llm
        return chain.invoke(converted_messages)


def code_model(request_body: RequestBody):
    model = "Phind/Phind-CodeLlama-34B-v2"
    llm = get_code_model(model=model, temprature=0, max_tokens=1000)
    messages= request_body.messages
    if messages:
        first_message = messages[0]
        if first_message.role != "system":
            messages.insert(0, Message(role="system", content=CODE_ASSISTANT_SYSTEM_PROMPT))
        first_message = messages.pop(0)
    
        prompt= ChatPromptTemplate.from_messages([
           (first_message.role, first_message.content),
           MessagesPlaceholder(variable_name='messages')
            ])
        formatted_messages = [(msg.role, msg.content) for msg in messages]
        converted_messages = convert_to_messages(formatted_messages)
        chain = prompt | llm
        return chain.invoke(converted_messages)



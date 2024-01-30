from token_helper import token_counter

TOKEN_LIMIT = 4096

def try_question_chat_history(prompt, question, history_messages):
    history_messages_str = '\n'.join(history_messages)
    prompt += f"""

    Following is user's question: {question}

    Following is the chat history: {history_messages_str}
    """
    return prompt
  
def add_question_chat_history(prompt, question, history_messages, model='gpt-4'):
    length = len(history_messages)
    while length > 0:
        result = try_question_chat_history(prompt, question, history_messages[0:length])
        if token_counter(result, model) < TOKEN_LIMIT:
            return result
        length -= 1
    prompt_lines = prompt.splitlines()
    lines = len(prompt_lines)
    while lines > 0:
        result = try_question_chat_history('\n'.join(prompt_lines[0:lines]), question, [])
        if token_counter(result, model) < TOKEN_LIMIT:
            return result
        lines -= 1
    return question


    

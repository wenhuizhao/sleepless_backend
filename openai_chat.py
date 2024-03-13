import os
import json
import time
from openai import OpenAI, OpenAIError
from pprint import pprint
from prompt_base import first_prompt,  get_instruction
from prompt_guest import get_guest_prompt
from prompt_user import get_user_prompt
from db_service import update_user, update_guest
from functions import update_sleep_info, update_sleep_diary

api_key = os.getenv("OPENAI_API_KEY")
agent_id = "asst_A1QMJgjMFvmrAuig4xUGur9h"
org_id = "org-7AIUiOtWmRBbz6yNBgOXNLUV"

client = OpenAI(
    organization = org_id,
    api_key = api_key
)
def process_message_with_citations(message):
    message_content = message.content[0].text.value
    return message_content


def handle_function(run, thread_id, user, guest, meta):
    print("handl_function")
    tools_to_call = run.required_action.submit_tool_outputs.tool_calls
    tools_output_array = []
    output = ""
    #print(tools_to_call)
    for each_tool in tools_to_call:
        tool_call_id = each_tool.id
        function_name = each_tool.function.name
        function_arg = each_tool.function.arguments
        print("Tool ID:" + tool_call_id)
        print("Function to Call:" + function_name )
        print("Parameters to use:" + function_arg)

        if (function_name == 'update_sleep_info'):
            output = update_sleep_info(function_arg, user, guest)
        elif (function_name == 'user_login'):
            meta['type'] = 'user_login'
            output = ""
        elif (function_name == 'update_sleep_diary'):
            output = update_sleep_diary(function_arg, user, guest)
        tools_output_array.append({"tool_call_id": tool_call_id, "output": output})

    client.beta.threads.runs.submit_tool_outputs(
        thread_id = thread_id,
        run_id = run.id,
        tool_outputs=tools_output_array
    )    


#tools = [{ "type": "retrieval"}]
#tools.append({"type": "function", "function": update_user_info})

def ask_question(question, new_session, history_messages, user=None, guest=None):
    meta = {}
    if new_session:
        thread = client.beta.threads.create()
        thread_id = thread.id
        if user:
            user.thread_id = thread.id
            update_user(user)
        if guest:
            guest.thread_id = thread.id
            update_guest(guest)
        prompt = first_prompt(question)
    else:
        if user:
            prompt = get_user_prompt(question=question, user=user, history_messages=history_messages)
            if user.thread_id:
                thread_id = user.thread_id
            else:
                thread = client.beta.threads.create()
                thread_id = thread.id
                user.thread_id = thread_id
                update_user(user)
        elif guest:
            prompt = get_guest_prompt(question, guest=guest, history_messages=history_messages)
            if guest.thread_id:
                print (f'thread id already exists, {guest.thread_id}')
                thread_id = guest.thread_id
            else:
                thread = client.beta.threads.create()
                thread_id = thread.id
                print (f'threadid, {thread_id}')
                guest.thread_id = thread_id
                update_guest(guest)

    print(f"threads.messages.create with  thread_id:{thread_id}")
    client.beta.threads.messages.create(
        thread_id = thread_id,
        role = "user",
        content = prompt
    )

    print(f"runs.create with  thread_id:{thread_id}, agent_id:{agent_id}")
    run = client.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = agent_id,
        instructions = get_instruction(question=question, user=user, guest=guest)
    )
    while run.status not in ["completed", "failed"]:
        print(f"check loop run.status:{run.status}, id:{run.id}")
        if run.status == "requires_action":
            handle_function(run, thread_id, user, guest, meta)
        time.sleep(3)
        run = client.beta.threads.runs.retrieve(
            thread_id = thread_id,
            run_id = run.id
        )

    print(f"run status: {run.status}")
    if run.status == 'failed':
        print (f"run, {run.last_error}")
        if (run.last_error.code == "rate_limit_exceeded"):
            return {"answers": "Our OpenAI credits are used up. Please try again later.", "meta": meta}
        return {"answers": "Something is wrong. Please try again.", "meta": meta}
    messages = client.beta.threads.messages.list(
        thread_id = thread_id
    )
    # print("collect run messages")
    # print(messages)
    assistant_messages_for_run = [
        message for message in messages 
        if message.run_id == run.id and message.role == "assistant"
    ]

    responses = map(lambda m: process_message_with_citations(m), assistant_messages_for_run)
    res= ""
    for r in responses:
        #print(f"response:{r}")
        res += r
    # print(f"responses:{res}")
    return { "answers": res, "meta": meta}
import os
import json
import time
from openai import OpenAI, OpenAIError
from prompt_base import first_prompt, get_instruction
from prompt_guest import get_guest_prompt
from prompt_user import get_user_prompt
from db_service import update_user, update_guest
from functions import update_sleep_info, update_sleep_diary

api_key = os.getenv("OPENAI_API_KEY")
agent_id = "asst_A1QMJgjMFvmrAuig4xUGur9h"
org_id = "org-7AIUiOtWmRBbz6yNBgOXNLUV"

client = OpenAI(
    organization=org_id,
    api_key=api_key,
    default_headers={
        "OpenAI-Beta": "assistants=v2"
    }
)

def process_message_with_citations(message):
    return message.content[0].text.value if message.content else ""

def handle_function(run, thread_id, user, guest, meta):
    print("handle_function")
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tools_output_array = []

    for call in tool_calls:
        tool_call_id = call.id
        function_name = call.function.name
        function_arg = call.function.arguments
        print(f"Tool ID: {tool_call_id}")
        print(f"Function to Call: {function_name}")
        print(f"Parameters to use: {function_arg}")

        if function_name == 'update_sleep_info':
            output = update_sleep_info(function_arg, user, guest)
        elif function_name == 'user_login':
            meta['type'] = 'user_login'
            output = ""
        elif function_name == 'update_sleep_diary':
            output = update_sleep_diary(function_arg, user, guest)
        else:
            output = ""

        tools_output_array.append({
            "tool_call_id": tool_call_id,
            "output": output
        })

    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run.id,
        tool_outputs=tools_output_array
    )

def ask_question(question, new_session, history_messages, user=None, guest=None):
    meta = {}

    if new_session:
        thread = client.beta.threads.create()
        thread_id = thread.id

        if user:
            user.thread_id = thread_id
            update_user(user)
        if guest:
            guest.thread_id = thread_id
            update_guest(guest)

        prompt = first_prompt(question)
    else:
        if user:
            prompt = get_user_prompt(question, user, history_messages)
            thread_id = user.thread_id or client.beta.threads.create().id
            if not user.thread_id:
                user.thread_id = thread_id
                update_user(user)
        elif guest:
            prompt = get_guest_prompt(question, guest, history_messages)
            thread_id = guest.thread_id or client.beta.threads.create().id
            if not guest.thread_id:
                guest.thread_id = thread_id
                update_guest(guest)

    print(f"threads.messages.create with thread_id: {thread_id}")
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    print(f"runs.create with thread_id: {thread_id}, assistant_id: {agent_id}")
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=agent_id,
        instructions=get_instruction(question, user, guest)
    )

    while run.status not in ["completed", "failed"]:
        print(f"Waiting... status: {run.status}, id: {run.id}")
        if run.status == "requires_action":
            handle_function(run, thread_id, user, guest, meta)

        time.sleep(3)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    print(f"Final run status: {run.status}")
    if run.status == "failed":
        print(f"Error: {run.last_error}")
        if run.last_error.code == "rate_limit_exceeded":
            return {"answers": "OpenAI credits are used up. Please try again later.", "meta": meta}
        return {"answers": "Something went wrong. Please try again.", "meta": meta}

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    assistant_messages = [
        m for m in messages.data
        if m.run_id == run.id and m.role == "assistant"
    ]

    response_texts = [process_message_with_citations(m) for m in assistant_messages]
    return {"answers": "".join(response_texts), "meta": meta}

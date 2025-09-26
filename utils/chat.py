from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from pypdf import PdfReader
from utils.logging import setup_logging


load_dotenv(override=True)
logger = setup_logging()

def chat_log(message, history):
    """Save each user and assistant message to a file after each generation.
    This is not a tool, it's just for logging.
    Args:
        message: The message to save.
        history: The chat history to save.
    """
    logger.info(f"Saving chat log: {message}")
    with open("chat_log.txt", "a") as f:
        f.write(f"User: {message}\n")
        f.write(f"Assistant: {history[-1]['content']}\n")

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {
        "type": "function",
        "name": record_user_details_json["name"],
        "description": record_user_details_json["description"],
        "parameters": record_user_details_json["parameters"],
    },
    {
        "type": "function",
        "name": record_unknown_question_json["name"],
        "description": record_unknown_question_json["description"],
        "parameters": record_unknown_question_json["parameters"],
    },
]

# Chat Completions-compatible tools schema
chat_tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]


class Me:

    def __init__(self):
        """Initialize persona context and OpenAI client.

        Loads `me/Profile.pdf` and `me/summary.txt` into memory for use in prompts.
        """
        self.openai = OpenAI()
        self.name = "Daniel Halwell"
        self.linkedin = ""
        try:
            reader = PdfReader("me/Profile.pdf")
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    self.linkedin += text
        except Exception as e:
            logger.error(f"Failed to read LinkedIn profile: {e}")
            self.linkedin = ""
        try:
            with open("me/summary.txt", "r", encoding="utf-8") as f:
                self.summary = f.read()
        except Exception as e:
            logger.error(f"Failed to read summary: {e}")
            self.summary = ""


    def handle_tool_call(self, tool_calls):
        """Execute streamed tool calls and return tool result messages.

        Args:
            tool_calls: Iterable of tool call objects containing name, arguments, and id.

        Returns:
            A list of tool result message dicts compatible with the OpenAI responses API.
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            logger.info(f"Tool called: {tool_name} with arguments: {arguments}")
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        """Construct the system prompt combining persona summary and LinkedIn text.

        Returns:
            The fully rendered system prompt string.
        """
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. \
Please give short answers and try to keep the conversation engaging and interesting and only engage in longer answers if the user asks for them. \
If the user is asking about a particular project, feel free to go into more detail about it. \
Remember to use the record_unknown_question tool if you don't know the answer to a question. \
For example, if the user asks you about your favorite color or your favorite movie or if they ask you about a coding language not specified in the context, you should use the record_unknown_question tool to record the question that you couldn't answer. \
If using the record_unknown_question tool, tell the user that I'd have to think about that and get back to you, 'ive let the other Dan know about that question and he'll get back to you soon.' \
Someone may ask how I would do a particular task, if I have done the task before, call upon the context to find out how I have done it in the past. If there is insufficient context, tell the user that you would have to think about that and get back to them. \
However, if I have it listed as something I have done, use the record_unknown_question tool to record the question that you couldn't answer and that I'd update the context to include the task later. Thank the user for the question and that you'd get back to them soon."

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt

    def chat_guardrails(self, message, history):
        """Return True if the user message is appropriate, False otherwise.

        Uses an LLM to classify sentiment and appropriateness without any
        allow/deny heuristics. Falls back to True on error.

        Args:
            message: The latest user message string.
            history: Prior conversation history (unused).

        Returns:
            Boolean indicating whether the message is appropriate.
        """
        system_msg = (
            "You are a sentiment and safety classifier. First assess sentiment "
            "(positive, neutral, or negative). Then determine if the message is "
            "appropriate for a general audience (no PII (with the exception of email), hate, harassment, sexual, "
            "or illegal content). Output only one token: 'True' if appropriate, "
            "or 'False' if not. Do not output anything else."
            "The only exception to PII is email, which is allowed if it's in the context of the conversation."
        )
        try:
            resp = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": message},
                ],
                temperature=0,
                max_tokens=3,
            )
            raw = (resp.choices[0].message.content or "").strip()
            cleaned = "".join(ch for ch in raw if ch.isalpha()).lower()
            verdict = True if cleaned == "true" else False if cleaned == "false" else True
            logger.info(f"Guardrails response: {raw} -> {verdict}")
            return verdict
        except Exception as e:
            logger.error("Guardrails call failed, defaulting to allowing the message")
            logger.error(f"Exception: {e}")
            return True
    
    def chat_guardrails_response(self):
        """Return a standard response for blocked (inappropriate) messages."""
        return (
            "I'm sorry, I can't answer that. Please ask a question that isn't "
            "about sensitive or inappropriate topics."
        )
    
    def chat(self, message, history):
        """Generator that streams a chat response and handles tool calls.

        Args:
            message: The latest user message string.
            history: Prior conversation history as a list of role/content dicts.

        Returns:
            Yields progressively longer assistant message strings for streaming UI updates.
        """
        # Sanitize incoming history to only include role/content pairs
        def _sanitize(msg):
            return {"role": msg.get("role"), "content": msg.get("content", "")}

        messages = (
            [{"role": "system", "content": self.system_prompt()}]
            + [
                _sanitize(m)
                for m in (history or [])
                if isinstance(m, dict) and m.get("role") in {"user", "assistant"}
            ]
            + [{"role": "user", "content": message}]
        )
        logger.info(f"User: {message}")
        if not self.chat_guardrails(message, history):
            yield self.chat_guardrails_response()
            return
        while True:
            stream = self.openai.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                tools=chat_tools,
                stream=True,
            )

            content_accumulated = ""
            streamed_tool_calls = {}
            finish_reason = None

            for event in stream:
                if not getattr(event, "choices", None):
                    continue
                choice = event.choices[0]
                delta = getattr(choice, "delta", None)
                if delta and getattr(delta, "content", None):
                    content_accumulated += delta.content
                    yield content_accumulated
                # Collect tool call deltas
                if delta and getattr(delta, "tool_calls", None):
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in streamed_tool_calls:
                            streamed_tool_calls[idx] = {
                                "id": getattr(tc, "id", None),
                                "name": None,
                                "arguments": "",
                            }
                        func = getattr(tc, "function", None)
                        if func and getattr(func, "name", None):
                            streamed_tool_calls[idx]["name"] = func.name
                        if func and getattr(func, "arguments", None):
                            streamed_tool_calls[idx]["arguments"] += func.arguments
                if getattr(choice, "finish_reason", None):
                    finish_reason = choice.finish_reason
                    break
            # If the model wants tool calls, execute them and continue the loop
            if finish_reason == "tool_calls" and streamed_tool_calls:
                # Build assistant tool_call message stub
                assistant_tool_msg = {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": item.get("id") or f"call_{idx}",
                            "type": "function",
                            "function": {
                                "name": item["name"],
                                "arguments": item.get("arguments", ""),
                            },
                        }
                        for idx, item in sorted(streamed_tool_calls.items())
                    ],
                }
                logger.info(f"Assistant tool message: {assistant_tool_msg}")
                # Convert to handle_tool_call inputs
                tool_calls_for_handler = []
                for idx, item in sorted(streamed_tool_calls.items()):
                    class ToolCall:
                        def __init__(self, name, arguments, id):
                            self.function = type("Function", (), {})()
                            self.function.name = name
                            self.function.arguments = arguments
                            self.id = id
                    logger.info(f"Tool call for handler: {item}")
                    tool_calls_for_handler.append(
                        ToolCall(
                            name=item["name"],
                            arguments=item.get("arguments", ""),
                            id=item.get("id") or f"call_{idx}",
                        )
                    )
                logger.info(f"Tool calls for handler: {tool_calls_for_handler}")
                results = self.handle_tool_call(tool_calls_for_handler)
                messages.append(assistant_tool_msg)
                messages.extend(results)
                logger.info(f"Messages: {messages}")
                chat_log(message, messages)
                continue

            logger.info(f"Assistant final response: {content_accumulated}")
            return
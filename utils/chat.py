from __future__ import annotations

from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from typing import List, Dict, Any, Optional

from utils.app_logging import setup_logging
from utils.vector_db import VectorDB


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
                "description": "The email address of this user",
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it",
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered",
            },
        },
        "required": ["question"],
        "additionalProperties": False,
    },
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
        """Initialize persona context, vector database, and OpenAI client."""
        self.openai = OpenAI()
        self.name = "Daniel Halwell"
        self.vector_db = VectorDB()
        self.system_context = self._build_system_context()
        self.email = "danielhalwell@gmail.com"

    def _build_system_context(self) -> str:
        """Render a concise persona context from vector store contents."""

        try:
            peek = self.vector_db.collection.peek(5)
            documents: List[str] = []
            metadatas: List[Dict[str, Any]] = []
            if isinstance(peek, dict):
                documents = peek.get("documents", []) or []
                metadatas = peek.get("metadatas", []) or []
        except Exception as exc:
            logger.error(f"Failed to peek vector DB: {exc}")
            documents, metadatas = [], []

        combined_entries: List[str] = []
        for text, metadata in zip(documents, metadatas):
            source = (
                metadata.get("source", "unknown")
                if isinstance(metadata, dict)
                else "unknown"
            )
            combined_entries.append(f"Source: {source}\n{text.strip()}")

        if not combined_entries:
            return (
                "You are Daniel Halwell, a scientist-turned-AI engineer who builds"
                " practical AI tooling, RAG systems, and automations. Be concise,"
                " professional, and acknowledge uncertainty when context is missing."
            )

        joined = "\n\n".join(combined_entries)
        return (
            "You are provided with an indexed knowledge base about Daniel Halwell."
            " Use it to answer questions faithfully.\n\n" + joined
        )

    def _compose_retrieval_query(
        self, message: str, history: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Combine current message with recent user turns for retrieval."""

        recent_user_msgs: List[str] = []
        if history:
            for item in reversed(history):
                if not isinstance(item, dict):
                    continue
                if item.get("role") == "user":
                    content = item.get("content", "") or ""
                    if content.strip():
                        recent_user_msgs.append(content.strip())
                if len(recent_user_msgs) >= 2:
                    break
        recent_user_msgs.reverse()
        if message.strip():
            recent_user_msgs.append(message.strip())
        return "\n\n".join(recent_user_msgs)

    def _build_retrieval_context(
        self, message: str, history: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Retrieve relevant knowledge snippets for the given message."""

        query = self._compose_retrieval_query(message, history)
        if not query:
            return ""

        try:
            results = self.vector_db.query(
                query,
                k=4,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.error(f"Vector DB query failed: {exc}")
            return ""

        documents = []
        metadatas = []
        distances = []
        if isinstance(results, dict):
            documents = (results.get("documents") or [[" "]])[0]
            metadatas = (results.get("metadatas") or [[{}]])[0]
            distances = (results.get("distances") or [[None]])[0]

        contexts: List[str] = []
        for idx, (doc, metadata) in enumerate(zip(documents, metadatas)):
            if not doc:
                continue
            source = "unknown"
            if isinstance(metadata, dict):
                source = metadata.get("source") or metadata.get("path") or "unknown"
                chunk_id = metadata.get("chunk_id")
                if chunk_id is not None:
                    source = f"{source}#chunk-{chunk_id}"
            score = distances[idx] if idx < len(distances) else None
            score_str = (
                f" (score: {score:.3f})" if isinstance(score, (int, float)) else ""
            )
            snippet = doc.strip().replace("\n\n", "\n")
            contexts.append(f"[{idx + 1}] Source: {source}{score_str}\n{snippet}")

        if not contexts:
            return ""

        return "Retrieved knowledge snippets:\n" + "\n\n".join(contexts)

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
            results.append(
                {
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                }
            )
        return results

    def system_prompt(self):
        """Construct the system prompt using persona context and vector DB summary."""

        return f"""
You are acting as {self.name}. You are answering questions on {self.name}'s website, particularly questions related to {self.name}'s career, background, skills and experience.
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. 
You have access to a retrieval system that stores vetted chunks about {self.name}. Always ground answers in those retrieved contexts.
Be professional and engaging, keeping responses concise unless a longer explanation is requested. If you cannot answer confidently, log the question via the record_unknown_question tool.
Encourage meaningful follow-up, suggesting email contact when appropriate. Reference where your context came from when it adds clarity.
My email is {self.email}.
Context preview:
{self.system_context}
"""

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
            verdict = (
                True if cleaned == "true" else False if cleaned == "false" else True
            )
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

        retrieval_context = self._build_retrieval_context(message, history)
        logger.info(f"Retrieval context: {retrieval_context}")

        messages = (
            [{"role": "system", "content": self.system_prompt()}]
            + (
                [
                    {
                        "role": "system",
                        "content": (
                            "Use the following retrieved snippets when forming your answer."
                            f" If they are empty, rely on your general knowledge of Daniel Halwell. If you don't know the answer, log the question via the record_unknown_question tool. My email is {self.email}.\n"
                            + retrieval_context
                        ),
                    }
                ]
                if retrieval_context
                else []
            )
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

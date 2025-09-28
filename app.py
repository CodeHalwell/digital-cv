def run_with_watch():
    from watchfiles import run_process

    logger.info("Starting watch mode on 'app' directory")

    def _run():
        logger.info("Reloading app.py")
        main()

    run_process(
        path=".",
        target=_run,
        watch_filter=lambda change, path: path.endswith(".py"),
    )
from dotenv import load_dotenv
import os
import gradio as gr
from utils.app_logging import setup_logging
from utils.chat import Me

load_dotenv(override=True)
logger = setup_logging()

logger.info("Starting digital-cv")

me = Me()
logger.info("Me initialized")
# Theming and chat styling for embedding
theme = gr.themes.Soft(primary_hue="indigo", neutral_hue="slate")
initial_assistant_message = (
    "Hello, nice to meet you! At any time, feel free to give me your name and email; "
    "I'll make a note and I can get back to you later."
)

chatbot = gr.Chatbot(
    label=None,
    avatar_images=("assets/logo.png", "assets/dan.png"),
    render_markdown=True,
    type="messages",
    value=[{"role": "assistant", "content": initial_assistant_message}],
    elem_id="chatbot",
)
logger.info("Chatbot initialized")
custom_css = """
html, body, .gradio-container { height: 100%; }
body {
    margin: 0;
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
    background: radial-gradient(circle at 10% 0%, #2f3c8f 0%, #171c37 55%, #0b1120 100%);
    color: #e7ecff;
}
.gradio-container {
    display: flex;
    background: transparent;
    padding: 28px 0 36px;
}
#container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 16px 24px 28px;
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    min-height: 0;
    border-radius: 20px;
    background: rgba(12, 20, 46, 0.82);
    box-shadow: 0 32px 60px rgba(4, 8, 24, 0.45);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(114, 135, 255, 0.24);
}
#header {
    align-items: center;
    gap: 18px;
    justify-content: flex-start;
}
#logo img {
    max-height: 210px;
    width: auto;
    border-radius: 18px;
    object-fit: contain;
    box-shadow: 0 18px 36px rgba(9, 12, 35, 0.4);
}
#intro-card {
    border-radius: 18px;
    padding: 20px 24px;
    background: linear-gradient(140deg, rgba(62, 78, 177, 0.42), rgba(24, 30, 64, 0.74));
    border: 1px solid rgba(140, 162, 255, 0.25);
    box-shadow: inset 0 0 0 1px rgba(210, 220, 255, 0.08);
}
#intro-card ul {
    margin: 0.35rem 0 0.7rem;
    padding-left: 1.1rem;
}
#intro-card li { margin-bottom: 0.3rem; }
#title {
    text-align: center;
    margin: 12px 0 14px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 650;
    color: #c6ceff;
}
#chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 16px;
    flex: 1 1 auto;
    min-height: 0;
}
#chatbot {
    display: flex;
    flex-direction: column;
    min-height: 520px;
    height: clamp(520px, calc(100dvh - 260px), 960px);
    border-radius: 20px;
    border: 1px solid rgba(142, 168, 255, 0.22);
    background: linear-gradient(165deg, rgba(25, 37, 76, 0.88), rgba(12, 18, 38, 0.95));
    box-shadow: inset 0 0 0 1px rgba(210, 220, 255, 0.05), 0 26px 48px rgba(7, 12, 34, 0.38);
}
#chatbot .wrapper,
#chatbot .bubble-wrap,
#chatbot .message-wrap {
    flex: 1 1 auto;
    display: flex;
    min-height: 0;
}
#chatbot .bubble-wrap {
    flex-direction: column;
    overflow-y: auto;
    padding: 6px 6px 12px;
}
#chatbot label span {
    color: rgba(221, 230, 255, 0.85);
    font-weight: 600;
    letter-spacing: 0.03em;
}
#chatbot .message-wrap .message {
    background: rgba(17, 27, 54, 0.88);
    border-radius: 16px;
    border: 1px solid rgba(140, 166, 255, 0.22);
    box-shadow: 0 16px 28px rgba(8, 14, 40, 0.32);
}
#chatbot .message-wrap .bot .message {
    background: linear-gradient(155deg, rgba(68, 99, 255, 0.28), rgba(18, 24, 50, 0.9));
}
#chatbot .message-wrap .user .message {
    background: linear-gradient(155deg, rgba(200, 108, 255, 0.32), rgba(24, 18, 44, 0.92));
}
.suggestion-banner {
    font-weight: 650;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 0.86rem;
    color: #aeb8ff;
}
.suggestion-buttons { display: flex; gap: 10px; flex-wrap: nowrap; justify-content: space-between; }
.suggestion-buttons button {
    flex: 1 1 0;
    min-width: 0;
    padding: 10px 12px;
    border-radius: 12px;
    border: 1px solid rgba(148, 174, 255, 0.35);
    background: linear-gradient(140deg, rgba(78, 103, 255, 0.24), rgba(30, 44, 110, 0.78));
    color: #f0f3ff;
    font-weight: 600;
    font-size: 0.92rem;
    transition: transform 0.17s ease, box-shadow 0.17s ease, border-color 0.17s ease;
}
.suggestion-buttons button:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 30px rgba(12, 20, 48, 0.42);
    border-color: rgba(193, 210, 255, 0.85);
}
.gradio-container textarea {
    border-radius: 14px !important;
    min-height: 90px !important;
    background: rgba(19, 28, 58, 0.94);
    border: 1px solid rgba(139, 162, 255, 0.3);
    color: #f2f4ff;
    box-shadow: inset 0 0 0 1px rgba(175, 196, 255, 0.1);
}
.gradio-container textarea:focus {
    outline: none;
    border-color: rgba(194, 208, 255, 0.92);
    box-shadow: 0 0 0 2px rgba(120, 148, 255, 0.34);
}
#footer {
    text-align: center;
    opacity: 0.9;
    font-size: 0.95rem;
    margin-top: 24px;
    letter-spacing: 0.04em;
}

@media (max-width: 900px) {
    #container { padding: 12px 18px; }
    #header { flex-direction: column; text-align: center; }
    #logo img { max-height: 170px; }
    #chatbot { height: clamp(460px, calc(100dvh - 220px), 820px); }
    .suggestion-buttons button { min-width: 150px; }
}

@media (max-width: 640px) {
    .gradio-container { padding: 18px 0 28px; }
    #container { border-radius: 18px; }
    #chatbot { height: clamp(420px, calc(100dvh - 200px), 720px); }
}
"""
logger.info("Custom CSS initialized")
with gr.Blocks(theme=theme, css=custom_css) as demo:
    with gr.Column(elem_id="container"):
        with gr.Row(elem_id="header"):
            with gr.Column(scale=2, min_width=140):
                gr.Image(
                    value="assets/Logo WO Background.png",
                    height=190,
                    show_label=False,
                    elem_id="logo",
                )
            with gr.Column(scale=10):
                with gr.Group(elem_id="intro-card"):
                    gr.Markdown(
                        """
                        **Welcome — Chat with Daniel**

                        - **What to ask**: projects, AI/RAG/agents, data pipelines, or career.
                        - **Privacy**: if you share an email, I’ll only save it when you ask.
                        - **Tip**: streaming is live; use Stop to interrupt and send a follow‑up.

                        Example prompts: “Tell me about your last role”, “How do you design a RAG pipeline?”, “Can you scope a small automation?”
                        """,
                    )
        gr.Markdown("## Chat with Daniel", elem_id="title")
        with gr.Column(elem_id="chat-wrapper"):
            chat_input = gr.Textbox(placeholder="Type your message…", autofocus=True)
            chat_iface = gr.ChatInterface(
                me.chat,
                type="messages",
                chatbot=chatbot,
                title="",
                description="Ask about projects, AI workflows, or get in touch.",
                submit_btn="Send",
                stop_btn="Stop",
                textbox=chat_input,
            )
            gr.Markdown("**Need inspiration?** Try asking:")
            with gr.Row(elem_classes="suggestion-buttons"):
                examples = [
                    "Tell me about your last role",
                    "How would you design a small RAG pipeline for docs?",
                    "What Python libraries are you familiar with?",
                ]
                for example in examples:
                    gr.Button(example).click(
                        lambda text=example: gr.update(value=text),
                        outputs=chat_input,
                    )
        gr.Markdown("Made with ❤️ — CoDHe Labs", elem_id="footer")
logger.info("Blocks app initialized")


def main():
    logger.info("Launching demo")
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        favicon_path="assets/logo.png",
        debug=True,
        show_error=True,
    )


if __name__ == "__main__":
    if os.getenv("WATCH_MODE") == "1":
        run_with_watch()
    else:
        main()
    logger.info("Demo launched")

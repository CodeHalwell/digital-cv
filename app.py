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
    font-family: "Inter", "SF Pro Display", "Segoe UI", system-ui, -apple-system, sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #1e293b 75%, #0f172a 100%);
    background-attachment: fixed;
    color: #f8fafc;
    font-feature-settings: "kern" 1, "liga" 1, "ss01" 1;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    font-weight: 400;
    line-height: 1.6;
}
.gradio-container {
    display: flex;
    background: transparent;
    padding: 28px 0 36px;
}
#container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 32px 40px 40px;
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    min-height: 0;
    border-radius: 32px;
    background: rgba(15, 23, 42, 0.95);
    box-shadow: 
        0 64px 128px rgba(0, 0, 0, 0.4),
        0 32px 64px rgba(0, 0, 0, 0.2),
        0 0 0 1px rgba(148, 163, 184, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(148, 163, 184, 0.15);
    position: relative;
    overflow: hidden;
}
#container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59, 130, 246, 0.6), 
        rgba(147, 51, 234, 0.6), 
        transparent
    );
    z-index: 1;
}
#container::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.05) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}
#header {
    align-items: center;
    gap: 32px;
    justify-content: flex-start;
    margin-bottom: 16px;
    position: relative;
    z-index: 2;
}
#logo img {
    max-height: 240px;
    width: auto;
    border-radius: 24px;
    object-fit: contain;
    box-shadow: 
        0 32px 64px rgba(0, 0, 0, 0.3),
        0 16px 32px rgba(0, 0, 0, 0.2),
        0 0 0 1px rgba(148, 163, 184, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    filter: brightness(1.05) contrast(1.1);
}
#logo img:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 
        0 48px 96px rgba(0, 0, 0, 0.4),
        0 24px 48px rgba(0, 0, 0, 0.3),
        0 0 0 1px rgba(59, 130, 246, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
    filter: brightness(1.1) contrast(1.15);
}
#intro-card {
    border-radius: 24px;
    padding: 32px 36px;
    background: linear-gradient(135deg, 
        rgba(30, 41, 59, 0.8) 0%, 
        rgba(51, 65, 85, 0.6) 50%, 
        rgba(30, 41, 59, 0.8) 100%
    );
    border: 1px solid rgba(148, 163, 184, 0.2);
    box-shadow: 
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        0 16px 32px rgba(0, 0, 0, 0.2),
        0 8px 16px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(16px);
}
#intro-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59, 130, 246, 0.5), 
        rgba(147, 51, 234, 0.5), 
        transparent
    );
}
#intro-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.03) 0%, transparent 70%);
    pointer-events: none;
}
#intro-card ul {
    margin: 0.35rem 0 0.7rem;
    padding-left: 1.1rem;
}
#intro-card li { margin-bottom: 0.3rem; }
#title {
    text-align: center;
    margin: 24px 0 32px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 800;
    color: #f1f5f9;
    font-size: 1.75rem;
    text-shadow: 
        0 4px 12px rgba(0, 0, 0, 0.4),
        0 2px 6px rgba(0, 0, 0, 0.2);
    position: relative;
    z-index: 2;
    background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
#title::after {
    content: '';
    position: absolute;
    bottom: -12px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 3px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59, 130, 246, 0.8), 
        rgba(147, 51, 234, 0.8), 
        transparent
    );
    border-radius: 2px;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
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
    min-height: 680px;
    height: clamp(680px, calc(100dvh - 200px), 1200px);
    border-radius: 28px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: linear-gradient(135deg, 
        rgba(15, 23, 42, 0.95) 0%, 
        rgba(30, 41, 59, 0.9) 50%, 
        rgba(15, 23, 42, 0.95) 100%
    );
    box-shadow: 
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        0 48px 96px rgba(0, 0, 0, 0.3),
        0 24px 48px rgba(0, 0, 0, 0.2),
        0 0 0 1px rgba(148, 163, 184, 0.1);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px);
    z-index: 2;
}
#chatbot::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59, 130, 246, 0.6), 
        rgba(147, 51, 234, 0.6), 
        transparent
    );
    z-index: 1;
}
#chatbot::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.02) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
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
    padding: 12px 16px 20px;
    gap: 16px;
}
#chatbot label span {
    color: rgba(221, 230, 255, 0.85);
    font-weight: 600;
    letter-spacing: 0.03em;
}
#chatbot .message-wrap .message {
    background: rgba(30, 41, 59, 0.9);
    border-radius: 24px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    box-shadow: 
        0 24px 48px rgba(0, 0, 0, 0.2),
        0 12px 24px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    padding: 20px 24px;
    margin: 8px 0;
    line-height: 1.6;
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
}
#chatbot .message-wrap .message::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}
#chatbot .message-wrap .message:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 
        0 32px 64px rgba(0, 0, 0, 0.3),
        0 16px 32px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
#chatbot .message-wrap .bot .message {
    background: linear-gradient(135deg, 
        rgba(30, 41, 59, 0.95) 0%, 
        rgba(51, 65, 85, 0.8) 100%
    );
    border-color: rgba(59, 130, 246, 0.3);
    margin-right: 60px;
    margin-left: 8px;
}
#chatbot .message-wrap .user .message {
    background: linear-gradient(135deg, 
        rgba(30, 41, 59, 0.95) 0%, 
        rgba(51, 65, 85, 0.8) 100%
    );
    border-color: rgba(147, 51, 234, 0.3);
    margin-left: 60px;
    margin-right: 8px;
}
.suggestion-banner {
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-size: 0.95rem;
    color: #cbd5e1;
    margin-bottom: 16px;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 2;
}
.suggestion-buttons { 
    display: flex; 
    gap: 16px; 
    flex-wrap: wrap; 
    justify-content: space-between; 
    margin-bottom: 12px;
    position: relative;
    z-index: 2;
}
.suggestion-buttons button {
    flex: 1 1 0;
    min-width: 0;
    padding: 16px 20px;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: linear-gradient(135deg, 
        rgba(30, 41, 59, 0.9) 0%, 
        rgba(51, 65, 85, 0.7) 100%
    );
    color: #f1f5f9;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    box-shadow: 
        0 8px 16px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
.suggestion-buttons button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59, 130, 246, 0.1), 
        transparent
    );
    transition: left 0.6s ease;
}
.suggestion-buttons button::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.2), 
        transparent
    );
}
.suggestion-buttons button:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 
        0 32px 64px rgba(0, 0, 0, 0.2),
        0 16px 32px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
    border-color: rgba(59, 130, 246, 0.5);
    background: linear-gradient(135deg, 
        rgba(30, 41, 59, 0.95) 0%, 
        rgba(51, 65, 85, 0.8) 100%
    );
}
.suggestion-buttons button:hover::before {
    left: 100%;
}
.suggestion-buttons button:active {
    transform: translateY(-2px) scale(1.01);
}
.gradio-container textarea {
    border-radius: 20px !important;
    min-height: 120px !important;
    background: rgba(30, 41, 59, 0.95) !important;
    border: 1px solid rgba(148, 163, 184, 0.3) !important;
    color: #f1f5f9 !important;
    box-shadow: 
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        0 16px 32px rgba(0, 0, 0, 0.2),
        0 8px 16px rgba(0, 0, 0, 0.1) !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    padding: 20px 24px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(16px) !important;
    position: relative !important;
    overflow: hidden !important;
}
.gradio-container textarea::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}
.gradio-container textarea:focus {
    outline: none !important;
    border-color: rgba(59, 130, 246, 0.6) !important;
    box-shadow: 
        0 0 0 4px rgba(59, 130, 246, 0.2),
        0 24px 48px rgba(0, 0, 0, 0.3),
        0 12px 24px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    background: rgba(30, 41, 59, 0.98) !important;
    transform: translateY(-1px) !important;
}
.gradio-container textarea::placeholder {
    color: rgba(203, 213, 225, 0.7) !important;
    font-weight: 500 !important;
    font-style: italic !important;
}
#footer {
    text-align: center;
    opacity: 0.8;
    font-size: 0.9rem;
    margin-top: 32px;
    letter-spacing: 0.06em;
    color: rgba(203, 213, 225, 0.8);
    font-weight: 500;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 2;
}

/* Professional loading states and animations */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}
.loading-message {
    animation: pulse 2s ease-in-out infinite;
}
.loading-shimmer {
    position: relative;
    overflow: hidden;
}
.loading-shimmer::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59, 130, 246, 0.1), 
        transparent
    );
    animation: shimmer 2.5s infinite;
}

/* Professional button styles */
.gradio-container button {
    border-radius: 16px !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 
        0 8px 16px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}
.gradio-container button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 
        0 16px 32px rgba(0, 0, 0, 0.2),
        0 8px 16px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
}
.gradio-container button:active {
    transform: translateY(-1px) scale(1.01) !important;
}

/* Professional scrollbar styling */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: rgba(30, 41, 59, 0.3);
    border-radius: 6px;
    border: 1px solid rgba(148, 163, 184, 0.1);
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, 
        rgba(59, 130, 246, 0.6) 0%, 
        rgba(147, 51, 234, 0.6) 100%
    );
    border-radius: 6px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, 
        rgba(59, 130, 246, 0.8) 0%, 
        rgba(147, 51, 234, 0.8) 100%
    );
    box-shadow: 
        0 4px 8px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

/* Professional responsive design */
@media (max-width: 1024px) {
    #container { 
        padding: 24px 32px; 
        border-radius: 28px;
        max-width: 100%;
    }
    #header { 
        gap: 24px;
    }
    #logo img { 
        max-height: 200px; 
    }
    #chatbot { 
        height: clamp(620px, calc(100dvh - 180px), 1000px); 
        border-radius: 24px;
    }
    #chatbot .message-wrap .bot .message {
        margin-right: 40px;
    }
    #chatbot .message-wrap .user .message {
        margin-left: 40px;
    }
}

@media (max-width: 900px) {
    #container { 
        padding: 20px 24px; 
        border-radius: 24px;
    }
    #header { 
        flex-direction: column; 
        text-align: center; 
        gap: 24px;
    }
    #logo img { 
        max-height: 180px; 
    }
    #chatbot { 
        height: clamp(580px, calc(100dvh - 160px), 900px); 
        border-radius: 20px;
    }
    #chatbot .message-wrap .bot .message {
        margin-right: 20px;
        padding: 16px 20px;
    }
    #chatbot .message-wrap .user .message {
        margin-left: 20px;
        padding: 16px 20px;
    }
    .suggestion-buttons { 
        flex-direction: column; 
        gap: 12px;
    }
    .suggestion-buttons button { 
        min-width: 100%; 
        padding: 16px 20px;
    }
    #title {
        font-size: 1.4rem;
        margin: 20px 0 24px;
    }
    #intro-card {
        padding: 24px 28px;
        border-radius: 20px;
    }
}

@media (max-width: 640px) {
    .gradio-container { 
        padding: 16px 0 24px; 
    }
    #container { 
        border-radius: 20px; 
        padding: 16px 20px;
    }
    #chatbot { 
        height: clamp(520px, calc(100dvh - 140px), 800px); 
        border-radius: 18px;
    }
    #chatbot .message-wrap .bot .message {
        margin-right: 12px;
        margin-left: 4px;
        padding: 14px 18px;
        border-radius: 20px;
    }
    #chatbot .message-wrap .user .message {
        margin-left: 12px;
        margin-right: 4px;
        padding: 14px 18px;
        border-radius: 20px;
    }
    #logo img { 
        max-height: 160px; 
    }
    #intro-card {
        padding: 20px 24px;
        border-radius: 16px;
    }
    .gradio-container textarea {
        min-height: 100px !important;
        padding: 16px 20px !important;
        font-size: 0.95rem !important;
        border-radius: 16px !important;
    }
    #title {
        font-size: 1.2rem;
        margin: 16px 0 20px;
    }
    .suggestion-buttons button {
        padding: 14px 18px;
        border-radius: 14px;
    }
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
            chat_input = gr.Textbox(
                placeholder="Type your message here…", 
                autofocus=True,
                max_lines=5,
                show_copy_button=True,
                container=False,
                scale=1
            )
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
            gr.Markdown("**Need inspiration?** Try asking:", elem_classes="suggestion-banner")
            with gr.Row(elem_classes="suggestion-buttons"):
                examples = [
                    "Tell me about your last role and what you do day to day",
                    "How would you design a small RAG pipeline for docs?",
                    "What Python libraries are you familiar with?",
                ]
                for example in examples:
                    gr.Button(
                        example,
                        variant="secondary",
                        size="sm"
                    ).click(
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

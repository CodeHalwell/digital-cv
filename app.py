from dotenv import load_dotenv
import os
import gradio as gr
from utils.logging import setup_logging
from utils.chat import Me

load_dotenv(override=True)
logger = setup_logging()

logger.info("Starting digital-cv")
    
me = Me()
logger.info("Me initialized")
# Theming and chat styling for embedding
theme = gr.themes.Soft(primary_hue="indigo", neutral_hue="slate")
chatbot = gr.Chatbot(
    label=None,
    avatar_images=("assets/logo.png", "assets/dan.png"),
    height=560,
    render_markdown=True,
    type="messages",
)
logger.info("Chatbot initialized")
custom_css = """
#container { max-width: 1100px; margin: 0 auto; padding: 8px 12px; }
#header { align-items: center; gap: 16px; justify-content: flex-start; }
#logo img { max-height: 200px; height: auto; width: auto; border-radius: 12px; object-fit: contain; }
#intro-card { border: 1px solid var(--border-color-primary); border-radius: 12px; padding: 14px 18px; background: var(--panel-background-fill); }
#intro-card ul { margin: 0.3rem 0 0.6rem; }
#title { text-align: center; margin: 8px 0 6px; }
#footer { text-align: center; opacity: 0.8; font-size: 0.9rem; }
/* Make the textbox and chat edges align nicely */
.gradio-container .gr-chatbot { border-radius: 12px; }
.gradio-container textarea { border-radius: 10px; }
"""
logger.info("Custom CSS initialized")
# Top header + explanation + chat in a single Blocks app
with gr.Blocks(theme=theme, css=custom_css) as demo:
    with gr.Column(elem_id="container"):
        with gr.Row(elem_id="header"):
            with gr.Column(scale=2, min_width=140):
                gr.Image(value="assets/Logo WO Background.png", height=190, show_label=False, elem_id="logo")
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
        gr.ChatInterface(
            me.chat,
            type="messages",
            chatbot=chatbot,
            title="",
            description="Ask about projects, AI workflows, or get in touch.",
            submit_btn="Send",
            stop_btn="Stop",
            examples=[
                ["Tell me about your last role"],
                ["How would you design a small RAG pipeline for docs?"],
                ["Can you scope a tiny automation for PDFs to JSON?"],
            ],
            textbox=gr.Textbox(placeholder="Type your message…", autofocus=True),
        )
        with gr.Row():
            gr.Button("Email Daniel", link="mailto:danielhalwell@gmail.com", variant="secondary")
            gr.Button("Business inquiries", link="mailto:codhe@codhe.co.uk", variant="secondary")
        gr.Markdown("Made with ❤️ — CoDHe Labs", elem_id="footer")
logger.info("Blocks app initialized")


if __name__ == "__main__":
    logger.info("Launching demo")
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        favicon_path="assets/logo.png",
        debug=False,
    )
    logger.info("Demo launched")
    
    
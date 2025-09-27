# Digital CV - Interactive Personal Assistant

An AI-powered digital CV that allows visitors to chat with Daniel Halwell through an intelligent conversational interface. Built with Gradio and powered by OpenAI's GPT models, this application provides an interactive way to learn about Daniel's professional background, experience, and capabilities.

## 🌟 Features

- **Interactive Chat Interface**: Natural language conversations about Daniel's experience, skills, and projects
- **Intelligent Context Awareness**: Draws from comprehensive professional summary and LinkedIn profile data
- **Contact Recording**: Ability to capture visitor contact information with proper consent
- **Professional Presentation**: Clean, responsive UI with custom branding
- **Question Tracking**: Logs unknown questions to continuously improve the knowledge base

## 🔧 Technology Stack

- **Frontend**: Gradio (Python-based web UI framework)
- **AI/LLM**: OpenAI GPT models with function calling
- **Document Processing**: PyPDF for resume parsing
- **Notifications**: Pushover integration for contact alerts
- **Deployment**: Supports containerized deployment
- **Python Version**: 3.11+

## 📁 Project Structure

```
digital-cv/
├── app.py                 # Main Gradio application
├── me/
│   ├── Profile.pdf       # LinkedIn profile export
│   └── summary.txt       # Comprehensive professional summary
├── utils/
│   ├── chat.py          # Core chat functionality and AI integration
│   ├── tool_calls.py    # Function calling tools (contact recording, etc.)
│   └── logging.py       # Application logging setup
├── assets/
│   ├── logo.png         # Application logo
│   ├── dan.png          # Avatar image
│   └── Logo WO Background.png
├── pyproject.toml       # Project dependencies and metadata
├── .env                 # Environment variables (create this file locally; not included in repo)
└── README.md           # This file
## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API key
- (Optional) Pushover account for notifications

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CodeHalwell/digital-cv.git
   cd digital-cv
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```
   
   Or install key dependencies directly:
   ```bash
   pip install gradio openai python-dotenv pypdf requests
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PUSHOVER_TOKEN=your_pushover_token (optional)
   PUSHOVER_USER=your_pushover_user_key (optional)
   PORT=7860
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the interface**
   Open your browser and navigate to `http://localhost:7860`

## 🎯 Usage

### For Visitors

- Start a conversation by typing questions about Daniel's experience, skills, or projects
- Example prompts:
  - "Tell me about your last role"
  - "How do you design a RAG pipeline?"
  - "What projects have you worked on?"
  - "Can you scope a small automation?"
- Share your contact information if you'd like to connect directly
- Use the "Stop" button to interrupt streaming responses

### For Developers

- The chat interface automatically draws context from `me/summary.txt` and `me/Profile.pdf`
- Function calling enables contact recording and question tracking
- All conversations are logged for analytics and improvement

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes |
| `PUSHOVER_TOKEN` | Pushover application token | No |
| `PUSHOVER_USER` | Pushover user key | No |
| `PORT` | Server port (default: 7860) | No |

### Customization

- **Personal Content**: Update `me/summary.txt` with your professional background
- **Profile**: Replace `me/Profile.pdf` with your LinkedIn export
- **Branding**: Update images in the `assets/` directory
- **Styling**: Modify the `custom_css` variable in `app.py`

## 🛡️ Features Deep Dive

### AI Chat System

The chat system uses OpenAI's GPT models with:
- **System prompts** that establish Daniel's professional persona
- **Function calling** for structured interactions (contact recording, question logging)
- **Content guardrails** to ensure appropriate conversations
- **Context injection** from professional documents

### Contact Management

When visitors share contact information:
- Details are validated and recorded via Pushover notifications
- Privacy-conscious approach - only records when explicitly shared
- Structured data capture (email, name, context notes)

### Question Tracking

Unknown or unanswerable questions are:
- Automatically detected and logged
- Sent via Pushover for manual review
- Used to continuously improve the knowledge base

## 📊 Monitoring & Analytics

- Application logs provide detailed interaction tracking
- Pushover notifications alert to new contacts and unknown questions
- Chat logs can be analyzed for common themes and improvements

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
The application is designed for containerized deployment:

```dockerfile
# Example Dockerfile approach
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["python", "app.py"]
```

### Deployment Considerations

- Set `debug=False` in production
- Use environment variables for all secrets
- Configure appropriate server limits for Gradio
- Consider using a reverse proxy (nginx) for production traffic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Update documentation as needed
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow existing code style and patterns
- Test changes with different conversation flows
- Update `me/summary.txt` if adding new professional information
- Ensure all dependencies are properly documented

## 📄 License

This project is personal intellectual property of Daniel Halwell. Contact for usage permissions.

## 📞 Contact

- **Email**: danielhalwell@gmail.com (personal) | codhe@codhe.co.uk (business)
- **GitHub**: [@CodeHalwell](https://github.com/CodeHalwell)
- **Portfolio**: [codehalwell.io](https://codehalwell.io)
- **LinkedIn**: [linkedin.com/in/danielhalwell](https://linkedin.com/in/danielhalwell)
- **Location**: Northwich, UK

## 🎨 About the Project

This digital CV represents a modern approach to professional networking and self-presentation. Rather than static resumes, it offers an interactive experience that showcases both technical capabilities and communication skills. The project demonstrates expertise in:

- AI/LLM integration and prompt engineering
- Modern Python web development with Gradio
- User experience design for professional applications
- Privacy-conscious data handling
- Scalable application architecture

---

*Made with ❤️ — CoDHe Labs*
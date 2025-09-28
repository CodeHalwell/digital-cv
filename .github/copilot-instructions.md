# GitHub Copilot Instructions for Digital CV

This document provides context and guidelines for GitHub Copilot when working on the Digital CV project.

## Project Overview

The Digital CV is an AI-powered conversational interface that represents Daniel Halwell's professional experience and capabilities. It's built using Gradio for the web interface and OpenAI's GPT models for natural language processing.

## Architecture & Key Concepts

### Core Components

1. **app.py**: Main Gradio application with UI definition and server setup
2. **utils/chat.py**: Contains the `Me` class that handles AI conversations, context loading, and function calling
3. **utils/tool_calls.py**: Implements function calling tools for contact recording and question tracking
4. **utils/logging.py**: Centralized logging configuration
5. **me/**: Directory containing Daniel's professional data (PDF resume, text summary)
6. **assets/**: Static assets (logos, images)

### Key Design Patterns

- **Context-Aware AI**: The system loads professional context from `me/summary.txt` and `me/Profile.pdf`
- **Function Calling**: Uses OpenAI's function calling for structured interactions (contact recording, question logging)
- **Streaming Responses**: Implements streaming chat for better user experience
- **Content Guardrails**: Built-in safety checks for conversation appropriateness
- **Privacy-First**: Only records contact information when explicitly provided by users

## Coding Guidelines

### Python Style

- Follow existing code patterns and naming conventions
- Use type hints where appropriate
- Maintain clear docstrings for functions and classes
- Error handling should be graceful and logged appropriately

### AI/LLM Integration

- **Model Selection**: Currently uses `gpt-5-mini` for main chat, `gpt-4o` for guardrails
- **System Prompts**: Located in `Me.system_prompt()` method - be careful when modifying
- **Function Calling**: Use the existing JSON schema patterns in `utils/chat.py`
- **Context Management**: Professional context is loaded once at initialization from files in `me/`

### Gradio UI

- **Theme**: Uses `gr.themes.Soft(primary_hue="indigo", neutral_hue="slate")`
- **Custom CSS**: Defined in `app.py` - maintain existing design patterns
- **Component Structure**: Logo + intro card layout, centralized chat interface
- **Responsive Design**: Ensure changes work on both desktop and mobile

### Environment & Configuration

- **Environment Variables**: Use `.env` file for configuration (never commit secrets)
- **Required**: `OPENAI_API_KEY`
- **Optional**: `PUSHOVER_TOKEN`, `PUSHOVER_USER`, `PORT`

## Development Workflows

### Adding New Features

1. **Chat Enhancements**: Modify `utils/chat.py` - particularly the `Me` class methods
2. **UI Changes**: Update `app.py` - be mindful of the custom CSS and layout
3. **New Tools**: Add function calling tools to `utils/tool_calls.py` and wire them in `utils/chat.py`
4. **Content Updates**: Modify files in `me/` directory for professional information changes

### Testing Approach

- **Manual Testing**: Run the app locally and test conversation flows
- **Function Testing**: Verify tool calling works correctly (contact recording, question logging)
- **UI Testing**: Check responsive design and visual components
- **Context Testing**: Ensure AI responses draw appropriately from professional context

### Common Tasks

#### Adding a New Function Call Tool

1. Define the function in `utils/tool_calls.py`
2. Create the JSON schema in `utils/chat.py`
3. Add to the `tools` and `chat_tools` arrays
4. Handle the function call in the chat loop

#### Updating Professional Context

1. **Structured Data**: Update `me/summary.txt` - this is the primary knowledge source
2. **PDF Resume**: Replace `me/Profile.pdf` with updated LinkedIn export
3. **Restart Required**: Changes to context files require application restart

#### UI Customization

1. **CSS**: Modify the `custom_css` variable in `app.py`
2. **Layout**: Update the Gradio component structure
3. **Assets**: Replace files in `assets/` directory for branding changes

## API & Dependencies

### Key Dependencies

- **gradio**: Web interface framework - be mindful of version compatibility
- **openai**: AI/LLM integration - function calling requires specific versions
- **pypdf**: PDF processing for resume parsing
- **python-dotenv**: Environment variable management
- **requests**: HTTP requests for Pushover notifications

### Version Considerations

- **Python**: Requires 3.11+
- **OpenAI**: Function calling syntax may change between versions
- **Gradio**: UI components and theming evolve frequently

## Security & Privacy

### Data Handling

- **Personal Data**: Only records contact info when explicitly provided
- **Logging**: Be careful about what gets logged - avoid sensitive information
- **API Keys**: Always use environment variables, never hardcode secrets

### Content Safety

- **Guardrails**: The `chat_guardrails()` method provides content filtering
- **Function Calling**: Validate inputs to function calls to prevent abuse
- **User Context**: Be mindful of what context is provided to the AI

## Common Issues & Solutions

### Installation Problems

- **Dependencies**: The `pyproject.toml` has many dependencies - minimal installs may work better
- **Python Version**: Ensure Python 3.11+ for compatibility

### Runtime Issues

- **OpenAI API**: Check API key configuration and rate limits
- **File Loading**: Ensure `me/` directory files are accessible
- **Port Conflicts**: Default port 7860 may need changing

### AI Behavior

- **Context Relevance**: Responses should draw from Daniel's professional background
- **Function Calling**: Tools should only trigger when appropriate
- **Conversation Flow**: Maintain professional tone while being approachable

## Best Practices When Using Copilot

1. **Context Awareness**: Reference existing patterns in the codebase
2. **Professional Focus**: Keep suggestions aligned with the CV's professional purpose
3. **Error Handling**: Include graceful error handling for external dependencies
4. **Documentation**: Update docstrings when modifying functions
5. **Testing**: Consider manual testing scenarios for AI-driven features

## Files to Be Especially Careful With

- **me/summary.txt**: Contains the core professional context - changes affect all AI responses
- **utils/chat.py**: Core AI logic - changes here impact the entire conversation system
- **app.py**: Main application entry point - UI changes affect user experience

## Deployment Considerations

- **Environment**: Production vs development environment variable management
- **Scaling**: Consider rate limits and concurrent users
- **Monitoring**: Ensure logging provides adequate visibility into system behavior

---

This document should help GitHub Copilot provide more contextually appropriate suggestions for the Digital CV project. Remember that this is a professional representation tool, so all suggestions should maintain that focus and quality standard.
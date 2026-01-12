# Chatter

`chatter` is a Python CLI tool for maintaining conversational context with AI chat models (ChatGPT, Copilot, etc.) in local markdown files. It uses a custom text-based chat script format that allows you to interact with multiple AI agents within a single file, with the CLI parsing conversation history and managing multi-turn context.

## Features

- **Text-based chat format**: Maintain conversations in human-readable markdown files
- **Multiple agent support**: Interact with ChatGPT, Copilot, or custom agents in the same conversation
- **Context preservation**: Full conversation history is maintained locally in markdown files
- **CLI interface**: Send messages and receive responses via command line
- **Vim integration**: Custom syntax highlighting and helper commands for editing chat files
- **Voice support**: Record audio and transcribe using OpenAI's Whisper API
- **Configurable**: Customize model selection and audio device preferences

## Installation

### Python Module and CLI

Install the `chatter` package using pip:

```bash
pip install -e .
```

Or install directly from the repository:

```bash
# Install from main branch
pip install git+https://github.com/bracket/chatter.git@main

# Or install a specific version/tag
pip install git+https://github.com/bracket/chatter.git@v0.1.0
```

This will install the `chatter` CLI command and all Python dependencies.

### Vim Plugin

To install the Vim plugin for `.chat` file support:

1. Copy the plugin files to your Vim configuration directory:

```bash
# For standard Vim
cp -r vim/* ~/.vim/

# For Neovim
cp -r vim/* ~/.config/nvim/
```

2. Alternatively, if you use a plugin manager like vim-plug, add to your `.vimrc`:

```vim
Plug 'bracket/chatter', {'rtp': 'vim/'}
```

The Vim plugin provides:
- Automatic filetype detection for `.chat` files
- Markdown syntax highlighting
- Helper commands for adding message blocks
- Integration with the `chatter` CLI

## Configuration

Create a configuration file at `~/.chatterrc` to customize chatter's behavior:

```yaml
# Chatter Configuration File
# Place this file in your home directory as ~/.chatterrc

openai:
  # Specify the OpenAI model to use
  # Default: gpt-4.1-mini
  model: gpt-4

voice:
  # Default audio input device index for recording
  # Use "chatter voice list-devices" to see available devices
  # Default: 0
  device_index: 0
```

You'll also need to set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or create a `.env` file in your working directory:

```
OPENAI_API_KEY=your-api-key-here
```

## Chat File Format

Chatter uses a custom markdown-based chat script format. Messages are identified by role prefixes:

```markdown
Me: This is my message to the AI.

ChatGPT: This is the AI's response.

Me: I can ask another question here.
This message can span multiple lines.

Copilot: You can also interact with different agents
in the same conversation.

<!-- :timestamp: 2024-06-20T10:00:00Z -->
Me: Messages can have optional metadata in HTML comments above them.
```

### Role Identifiers

- `Me:` - User messages
- `ChatGPT:` - Responses from ChatGPT
- `Copilot:` - Responses from Copilot (or any custom agent)

### Escape Sequences

If you need to include literal role identifiers in message content, prefix them with an extra colon:

```markdown
Me: I want to talk about the ::Me: prefix format.
```

This will be displayed as `Me: prefix format` in the actual content.

### Metadata

Messages can include optional metadata in HTML comments above the message:

```markdown
<!-- :timestamp: 2024-06-20T10:00:00Z -->
<!-- :role: assistant -->
ChatGPT: This message has metadata.
```

## CLI Usage

### Basic Chat Interaction

Send a chat file to an AI agent and get a response:

```bash
# Read from file, write to stdout
chatter chat conversation.chat

# Read from stdin, write to stdout
echo "Me: Hello, how are you?" | chatter chat

# Read from file, append response to the same file
chatter chat conversation.chat -o conversation.chat

# Use full history mode (output entire conversation)
chatter chat conversation.chat -f -o conversation.chat
```

### Chat Options

```bash
# Specify which agent to use
chatter chat input.chat -a Copilot

# Add timestamp metadata to responses
chatter chat input.chat -t

# Add newlines before the response
chatter chat input.chat -n 2

# Enable verbose logging
chatter chat input.chat -v

# Combine options
chatter chat input.chat -f -t -n 1 -o output.chat
```

### Voice Commands

Record and transcribe audio:

```bash
# List available audio input devices
chatter voice list-devices

# Record audio from default microphone
chatter voice record -o recording.flac

# Record from specific device
chatter voice record -o recording.flac -d 1

# Transcribe audio file
chatter voice transcribe -i recording.flac

# Transcribe with specific model
chatter voice transcribe -i recording.flac --model whisper-1
```

### Example Workflow

```bash
# 1. Create a new chat file
echo "Me: What is the capital of France?" > chat.chat

# 2. Get a response and save to a new file
chatter chat chat.chat -f -t -n 1 -o chat_with_response.chat

# 3. Continue the conversation by adding to the response file
echo -e "\nMe: What about Germany?" >> chat_with_response.chat

# 4. Get another response
chatter chat chat_with_response.chat -f -t -n 1 -o chat_final.chat

# Alternatively, you can overwrite the same file (use with caution):
# chatter chat conversation.chat -f -t -n 1 -o conversation.chat
```

## Vim Usage

The Vim plugin provides commands and key mappings for working with `.chat` files.

### Commands

- `:ChatterSend` - Send the current buffer to the chatter CLI and append the response
- `:ChatterAddMe` - Add or navigate to a "Me:" message block
- `:ChatterAddCopilot` - Add or navigate to a "Copilot:" message block

### Key Mappings

- `<leader>cs` - Send buffer to Chatter (equivalent to `:ChatterSend`)
- `<leader>ca` - Add/navigate to "Me:" block (equivalent to `:ChatterAddMe`)
- `<leader>cc` - Add/navigate to "Copilot:" block (equivalent to `:ChatterAddCopilot`)

### Example Vim Workflow

1. Open or create a `.chat` file:
   ```bash
   vim conversation.chat
   ```

2. Press `<leader>ca` to start a new "Me:" message block

3. Type your message, then press ESC to return to normal mode

4. Press `<leader>cs` to send the conversation to ChatGPT

5. The response will be appended to your file automatically

6. Press `<leader>ca` again to add another message

### Vim Configuration

The plugin automatically:
- Detects `.chat` files and sets the filetype
- Applies Markdown syntax highlighting
- Sets text width to 80 characters
- Enables line wrapping and spell checking

You can customize these settings in your `.vimrc` if needed.

## License

MIT

## Repository

https://github.com/bracket/chatter

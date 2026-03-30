# Phantom Visible Scripter 🎬

A local-first autonomous AI agent that researches topics and creates engaging YouTube scripts using entirely local infrastructure.

## 🎯 Features

- **Local-First**: Runs entirely on your machine using Ollama
- **Research Agent**: Gathers information from the web using DuckDuckGo
- **Planning Agent**: Creates structured content plans with user approval
- **Scripting Agent**: Generates engaging, conversational YouTube scripts
- **Feedback Loop**: Refine hooks, sections, and entire scripts interactively
- **No API Keys**: Uses free DuckDuckGo search instead of paid APIs

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull LLaMA 3 model**:
   ```bash
   ollama pull llama3.1:8b
   ```

3. **Start Ollama server**:
   ```bash
   ollama serve
   ```

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd PhantomVisibleScriptor
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create activation shortcut (optional):
   ```bash
   # Add this to your ~/.bashrc or ~/.zshrc for quick activation
   alias activate-pvs="cd /home/phantomvisible/Documents/GitHub/PhantomVisibleScriptor && source langchain-env/bin/activate"
   
   # Then simply run:
   activate-pvs
   ```

### Usage

#### Basic Usage

```bash
python main.py "your youtube topic here"
```

#### Advanced Options

```bash
# Use different model
python main.py "productivity tips" --model llama3.1:8b

# Custom Ollama server
python main.py "machine learning basics" --url http://localhost:11435

# Interactive mode (will prompt for topic)
python main.py
```

## 🏗️ Architecture

```
Phantom Visible Scripter
├── Input Stage
│   └── User provides topic via CLI
├── Research Agent
│   ├── DuckDuckGo web search
│   ├── Content extraction
│   └── Research synthesis
├── Planning Agent
│   ├── Hook generation
│   ├── Section planning
│   └── Narrative flow design
├── Scripting Agent
│   ├── Full script generation
│   ├── Tone optimization
│   └── Length targeting
└── Feedback Loop
    ├── Hook refinement
    ├── Section editing
    └── Script regeneration
```

## 📁 Project Structure

```
PhantomVisibleScriptor/
├── main.py                 # Main CLI interface
├── agents/
│   ├── research_agent.py   # Web research and synthesis
│   ├── planning_agent.py   # Content plan creation
│   └── scripting_agent.py  # Script generation
├── tools/
│   └── search.py          # DuckDuckGo search implementation
├── utils/
│   └── ollama_client.py   # Ollama integration
├── prompts/
│   ├── research_prompt.txt
│   ├── planning_prompt.txt
│   └── scripting_prompt.txt
├── requirements.txt
└── README.md
```

## 🎬 Script Generation Pipeline

### 1. Research Phase
- Searches DuckDuckGo for relevant sources
- Extracts content from top 5-10 results
- Synthesizes into structured research notes
- Identifies key insights, examples, and statistics

### 2. Planning Phase
- Generates compelling hook options
- Creates logical video sections
- Designs narrative flow
- Estimates video duration and word count
- **Awaits user approval**

### 3. Scripting Phase
- Generates full 10-15 minute script
- Maintains conversational, motivational tone
- Includes smooth transitions
- Targets 1500-2500 words

### 4. Refinement Phase
- Regenerate hooks based on feedback
- Refine specific sections
- Generate alternative scripts
- Save final script to file

## 🔧 Refinement Options

After script generation, you can refine your content through multiple options:

1. **Regenerate Hooks**: Create new opening hooks based on feedback
2. **Refine Specific Section**: Improve particular sections of the script
3. **Generate Alternative Script**: Create a completely new version
4. **Save Script**: Export your script to a text file
5. **Show Research Sources**: View all sources used in research
6. **Collaborative Improvement** 🆕: AI discusses with AI to improve the script *(Optional)*
7. **Exit**: Leave the application

#### **Collaborative Improvement Process:**

When you choose option 6, the system initiates a unique multi-model collaboration:

1. **Self-Analysis**: The primary model analyzes its own work honestly
2. **Peer Review**: A second AI model reviews the script and analysis
3. **Consensus Building**: Models discuss and reach agreement on improvements
4. **Implementation**: Generate improved version based on collaborative recommendations

**Note**: This feature is optional and gracefully handles cases where collaborative agent initialization fails. You can still use all other features normally!

This feature ensures multiple AI perspectives lead to better, more refined scripts!

## 🎯 Script Characteristics

- **Length**: 10-15 minutes (1500-2500 words)
- **Tone**: Conversational, motivational, authentic
- **Structure**: Strong hook → logical sections → compelling conclusion
- **Style**: Natural language, engaging questions, smooth transitions
- **Avoids**: Clickbait, clichés, cringe phrases, salesy language

## 🔧 Configuration

### Ollama Settings

Default configuration in `utils/ollama_client.py`:
- Model: `llama3.1:8b`
- URL: `http://localhost:11434`
- Temperature: `0.7`
- Top P: `0.9`
- Top K: `40`

### Search Settings

Default search configuration in `tools/search.py`:
- Max results: `10`
- Content length: `5000` characters
- Source limit: `8` websites

## 🛠️ Development

### Adding New Agents

1. Create new agent class in `agents/`
2. Inherit from base patterns in existing agents
3. Use `OllamaClient` for LLM interactions
4. Update `main.py` to integrate new agent

### Customizing Prompts

Edit prompt templates in `prompts/`:
- `research_prompt.txt`: Research synthesis guidelines
- `planning_prompt.txt`: Content planning instructions  
- `scripting_prompt.txt`: Script generation style

### Testing

```bash
# Test Ollama connection
python -c "from utils.ollama_client import OllamaClient; print(OllamaClient().test_connection())"

# Test search functionality
python -c "from tools.search import DuckDuckGoSearch; print(len(DuckDuckGoSearch().search('test')))"
```

## 🐛 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve

# Check model availability
ollama show llama3.1:8b
```

### Search Issues

- DuckDuckGo may rate-limit requests
- Some websites block scraping
- Use VPN if search results are limited

### Script Quality

- Adjust temperature in `ollama_client.py` for more/less creativity
- Edit prompts in `prompts/` for different styles
- Provide specific feedback in refinement phase

## 📝 Examples

### Basic Usage
```bash
python main.py "the benefits of morning routines"
```

### With Custom Model
```bash
python main.py "artificial intelligence ethics" --model llama3.1:8b
```

### Development Mode
```bash
python main.py "how to learn programming faster" --url http://192.168.1.100:11434
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

## 📄 License

This project is open source. Check LICENSE file for details.

## 🙏 Acknowledgments

- Ollama team for local LLM infrastructure
- DuckDuckGo for privacy-focused search
- LangChain for LLM orchestration
- YouTube creators who inspired this workflow

---

**Made with ❤️ for content creators who value privacy and control**

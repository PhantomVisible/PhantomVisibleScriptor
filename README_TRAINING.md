# 🎯 Training Your Models on Previous Scripts

This guide shows how to train Phantom Visible Scripter to mimic your unique writing style using your existing scripts.

## 📁 Setup

### 1. Organize Your Scripts
```
PhantomVisibleScriptor/
├── previous_work/
│   ├── script1.docx
│   ├── script2.docx
│   └── script3.docx
└── training_data/    # Will be created automatically
```

### 2. Install Training Dependencies
```bash
pip install python-docx
```

## 🚀 Training Pipeline

### Step 1: Extract Style Patterns
```bash
python training_data_processor.py
```

**What it does:**
- Reads all .docx files in `previous_work/`
- Extracts stylistic patterns (hooks, transitions, vocabulary)
- Analyzes your unique writing style
- Creates `training_data/style_dataset.json`

**Output:**
- Hook patterns you commonly use
- Transition words and phrases
- Average script length
- Vocabulary diversity
- Common rhetorical devices

### Step 2: Create Style Guide
```bash
python style_trainer.py
```

**What it does:**
- Converts training data into style guide
- Identifies your signature patterns
- Creates `training_data/style_guide.txt`
- Tests style generation with sample topic

### Step 3: Integrate with ScriptingAgent

#### Option A: Manual Integration
Update `prompts/scripting_prompt.txt` to include:

```text
STYLE REQUIREMENTS:
- Write in the style documented in training_data/style_guide.txt
- Use these hook patterns: [extracted from your scripts]
- Use these transitions: [extracted from your scripts]
- Maintain this average word count: [your average]
- Keep this conversational tone: [your voice]
```

#### Option B: Automatic Integration
Modify `agents/scripting_agent.py` to load your style dynamically:

```python
def _load_user_style(self):
    with open("training_data/style_guide.txt", "r") as f:
        return f.read()

def generate_script(self, research_data, content_plan):
    # Load your style
    user_style = self._load_user_style()
    
    # Add to system prompt
    system_prompt = f"""You are a professional YouTube script writer.
{user_style}"""
    
    # Generate with your style
    prompt = self._prompt_template.format(
        topic=topic,
        plan=plan,
        script=script
    )
    
    response = self.ollama.generate_response(prompt, system_prompt)
    return response
```

## 📊 Style Analysis Features

The training extracts these patterns from your scripts:

### **Hook Patterns**
- Question-based hooks ("What if I told you...")
- Contrarian statements ("The truth about X is...")
- Personal anecdotes ("Let me tell you about...")
- Surprising statistics ("Did you know that...")

### **Transition Words**
- Sequential connectors ("Now, let's talk about...")
- Contrast words ("But here's the thing...")
- Rhetorical questions ("So what does this mean?")

### **Vocabulary Analysis**
- Word diversity score
- Technical vs casual language balance
- Sentence length variation
- Question/exclamation ratio

### **Structural Patterns**
- Average paragraph count
- Hook-to-content ratio
- Conclusion styles
- Call-to-action approaches

## 🎯 Benefits of Style Training

### **Consistency**
- All generated scripts sound like you
- Maintains your unique voice
- Preserves your rhetorical devices

### **Efficiency**
- Reduces post-generation editing
- Captures your proven formulas
- Maintains your engagement patterns

### **Quality**
- Based on your successful content
- Preserves what works for your audience
- Maintains your brand voice

## 🔄 Continuous Learning

### **Retraining**
Add new scripts to `previous_work/` and rerun:
```bash
python training_data_processor.py
```

### **Style Evolution**
Your style guide evolves as you add more scripts:
- Early scripts: Foundation patterns
- Recent scripts: Current preferences
- Mix: Balanced style evolution

## 🚨 Troubleshooting

### **Common Issues**
- **"No .docx files found"** → Add scripts to `previous_work/`
- **"python-docx not installed"** → Run `pip install python-docx`
- **"Empty training data"** → Check script content extraction

### **Style Not Matching**
If generated scripts don't sound like you:
1. Add more diverse examples to `previous_work/`
2. Include different script types (tutorials, opinions, stories)
3. Run training pipeline again
4. Manually adjust `training_data/style_guide.txt`

## 🎪 Advanced Usage

### **A/B Testing**
Create multiple style guides:
```bash
# Training for different content types
python training_data_processor.py  # Extract all scripts
# Then manually create separate style guides for:
# - Tutorial style
# - Opinion style  
# - Storytelling style
```

### **Style Blending**
Combine your style with best practices:
```python
# In scripting_agent.py
def generate_script(self, research_data, content_plan, blend_with_best_practices=True):
    user_style = self._load_user_style()
    
    if blend_with_best_practices:
        system_prompt = f"""You are a professional YouTube script writer.
        
        {user_style}
        
        Additionally, follow these best practices:
        - Strong hook in first 15 seconds
        - Clear structure with smooth transitions
        - Actionable takeaways
        - Conversational, authentic tone"""
    else:
        system_prompt = f"""You are a professional YouTube script writer.
        {user_style}"""
```

This creates a hybrid approach: your unique voice + proven YouTube best practices!

## 🎯 Next Steps

1. **Process your scripts**: `python training_data_processor.py`
2. **Generate style guide**: `python style_trainer.py`  
3. **Test the style**: Interactive testing in style trainer
4. **Integrate**: Update ScriptingAgent or prompts
5. **Generate**: `python main.py "your topic"`

Your Phantom Visible Scripter will then write scripts in YOUR unique style! 🚀

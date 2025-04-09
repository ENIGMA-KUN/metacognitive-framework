# Metacognitive Analysis Framework for LLMs

## 📚 Project Overview

The Metacognitive Analysis Framework is a comprehensive system for evaluating how well Large Language Models (LLMs) demonstrate metacognitive capabilities - essentially, how well they "think about their thinking." Unlike traditional evaluation frameworks that focus primarily on factual accuracy, this framework analyzes the reasoning process itself, providing nuanced confidence scores for LLM outputs based on their metacognitive abilities.

The framework analyzes five key dimensions:

1. **Knowledge Awareness** (w₁ = 0.25) - How well models recognize what they know versus don't know
2. **Reasoning Quality** (w₂ = 0.25) - The logical structure and validity of the reasoning process
3. **Uncertainty Calibration** (w₃ = 0.20) - Alignment between expressed confidence and actual accuracy
4. **Self-Monitoring** (w₄ = 0.15) - Ability to detect and correct own errors
5. **Domain Adaptation** (w₅ = 0.15) - How well the model adjusts its reasoning approach based on domain

## 🏗️ Framework Architecture

```
metacognitive_framework/
│
├── config/
│   └── weights.py          # Configuration for dimension and metric weights
│
├── core/
│   ├── __init__.py
│   ├── base_evaluator.py   # Abstract base class for all evaluators
│   ├── dimension.py        # Class representing a framework dimension
│   ├── metric.py           # Class representing an evaluation metric
│   └── framework.py        # Main framework class that combines all dimensions
│
├── dimensions/
│   ├── __init__.py
│   ├── knowledge_awareness/
│   │   ├── __init__.py
│   │   ├── evaluator.py    # Knowledge Awareness evaluator
│   │   └── metrics.py      # Knowledge Awareness metrics implementation
│   ├── reasoning_quality/
│   │   ├── __init__.py
│   │   ├── evaluator.py    # Reasoning Quality evaluator 
│   │   └── metrics.py      # Reasoning Quality metrics implementation
│   ├── uncertainty_calibration/
│   │   ├── __init__.py
│   │   ├── evaluator.py    # Uncertainty Calibration evaluator
│   │   └── metrics.py      # Uncertainty Calibration metrics implementation
│   ├── self_monitoring/
│   │   ├── __init__.py
│   │   ├── evaluator.py    # Self-Monitoring evaluator
│   │   └── metrics.py      # Self-Monitoring metrics implementation
│   └── domain_adaptation/
│       ├── __init__.py
│       ├── evaluator.py    # Domain Adaptation evaluator
│       └── metrics.py      # Domain Adaptation metrics implementation
│
├── utils/
│   ├── __init__.py
│   ├── llm_interface.py    # Interface for interacting with LLMs (Claude)
│   ├── parsing.py          # Utilities for parsing LLM responses
│   └── visualization.py    # Tools for visualizing results
│
├── data/
│   ├── problems/           # Test problems for evaluation
│   ├── mock_responses/     # Mock responses for testing without API
│   └── results/            # Evaluation results
│
└── main.py                 # Main script to run the framework
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Setup Steps

1. Clone the repository (or create directories manually):
   ```bash
   # Create main directory structure (if not already done)
   mkdir -p metacognitive_framework/data/{problems,mock_responses,results}
   ```

2. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install numpy requests
   ```

4. (Optional) Set up your LLM API key:
   ```bash
   # For Windows PowerShell
   $env:ANTHROPIC_API_KEY = "your-api-key-here"
   
   # For Windows Command Prompt
   set ANTHROPIC_API_KEY=your-api-key-here
   
   # For Linux/Mac
   export ANTHROPIC_API_KEY=your-api-key-here
   ```

## 🚀 Usage

### Generate Test Data
```bash
python main.py --generate-data
```

### Run with Mock LLM Provider (Default)
```bash
python main.py --provider mock --num-samples 5
```

### Run with Claude API (Requires API Key)
```bash
python main.py --provider claude --api-key your-api-key-here --num-samples 5
```

### Command-Line Arguments
- `--provider`: LLM provider to use ('claude' or 'mock', default: 'mock')
- `--api-key`: API key for LLM provider (required when using 'claude')
- `--data-dir`: Directory containing test data (default: 'data/problems')
- `--output-dir`: Directory to save evaluation results (default: 'data/results')
- `--mock-dir`: Directory for mock responses (default: 'data/mock_responses')
- `--dimension`: Dimension to evaluate (default: 'knowledge_awareness')
- `--num-samples`: Number of samples to evaluate per metric (default: 5)
- `--generate-data`: Generate test data before evaluation

## ✅ Implementation Checklist

### Core Components
- [x] Project structure
- [x] Configuration for dimension and metric weights
- [x] Base evaluator class
- [x] Dimension class
- [x] Metric class
- [x] Main framework class
- [x] LLM interface with mock provider
- [x] LLM interface with Claude provider
- [x] Parsing utilities for LLM responses
- [x] Data generator for test datasets

### Dimensions (5)
1. Knowledge Awareness (w₁ = 0.25)
   - [x] Knowledge Boundary Recognition (30%)
   - [x] Source Attribution (25%)
   - [x] Temporal Awareness (25%)
   - [x] Hallucination Rate (20%)
   - [x] Overall dimension score calculation

2. Reasoning Quality (w₂ = 0.25)
   - [ ] Logical Consistency (25%)
   - [ ] Inference Validity (25%)
   - [ ] Step Completeness (20%)
   - [ ] Evidence Utilization (15%)
   - [ ] Causal Reasoning (15%)
   - [ ] Overall dimension score calculation

3. Uncertainty Calibration (w₃ = 0.20)
   - [ ] Confidence Calibration (35%)
   - [ ] Confidence Distribution (25%)
   - [ ] Probabilistic Expression (25%)
   - [ ] Ambiguity Recognition (15%)
   - [ ] Overall dimension score calculation

4. Self-Monitoring (w₄ = 0.15)
   - [ ] Error Detection Rate (30%)
   - [ ] Verification Attempts (25%)
   - [ ] Alternative Solution Exploration (25%)
   - [ ] Assumption Declaration (20%)
   - [ ] Overall dimension score calculation

5. Domain Adaptation (w₅ = 0.15)
   - [ ] Domain Recognition (25%)
   - [ ] Terminology Precision (25%)
   - [ ] Method Selection (25%)
   - [ ] Expert Mimicry (25%)
   - [ ] Overall dimension score calculation

### Visualization & Analysis
- [ ] Score dashboard for all dimensions
- [ ] Comparative analysis across models
- [ ] Detailed report generation
- [ ] Error analysis tools

## 📝 Mock vs. Real LLM API Considerations

The framework supports both mock LLM responses and real API calls (currently Claude API). Some considerations:

### Mock Provider Benefits:
- **Cost-free development**: No API credits required during development
- **Fast development**: No waiting for API responses or dealing with rate limits
- **Controlled testing**: Predictable responses for testing specific behaviors
- **Complete control**: Can craft responses to test edge cases

### Mock Provider Limitations:
- **Limited accuracy**: Mock responses don't perfectly mimic real LLM behavior
- **Less variability**: Lacks the subtle variations in real LLM outputs
- **Testing bias**: May lead to overfitting the evaluation system to mock patterns

### Recommended Approach:
1. **Development Phase**: Use mock provider to build and test the complete framework
2. **Validation Phase**: Test with limited real API calls to validate metrics
3. **Production Phase**: Use real LLM API for actual evaluations

The current implementation keeps the interface consistent between mock and real providers, allowing easy switching for testing and validation.


## 🔗 Additional Resources

The Metacognitive Analysis Framework is inspired by key academic and industry research on LLM evaluation, including:

- Uncertainty in Natural Language Processing (Xiao & Wang)
- Training Verifiers to Solve Math Word Problems (Cobbe et al.)
- Metacognition for AI Safety (Johnson)
- Reflexion: Language Agents with Verbal Reinforcement Learning (Shinn et al.)
- On the Dangers of Stochastic Parrots (Bender et al.)
- Measuring Massive Multitask Language Understanding (Hendrycks et al.)
- Large Language Models Can Self-Improve (Huang et al.)
- Language Models that Seek for Knowledge (Shuster et al.)
- Do Large Language Models Know What They Don't Know? (Yin et al.)
- Calibrated Language Models Must Hallucinate (Lin et al.)
- DeepSeek-R1 paper showing emergent metacognitive behaviors

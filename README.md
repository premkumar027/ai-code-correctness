# AI Code Correctness & Usability

Evaluating correctness and usability of AI-generated code across multiple LLMs.

## What is this?

A Streamlit-based tool that sends the same coding task to multiple LLMs and compares their outputs. Code correctness is verified via Python test cases and Lean 4 formal proofs.

## Models

- GPT-5.5 / GPT-5.4-mini (OpenAI)
- Claude Opus 4.7 / Claude Sonnet 4.6 (Anthropic)
- Gemini 3.1 Pro / Gemini 3 Flash (Google)
- Gemma 4 27B (Google, open-source)
- DeepSeek V4 Pro (open-source)

## Tasks

Dijkstra, BFS, Merge Sort, Binary Search, Prefix-Suffix Split — each in Python and Lean 4, with 3 prompt styles (naive, structured, chain-of-thought).

## Setup

```bash
git clone https://github.com/premkumar027/ai-code-correctness.git
cd ai-code-correctness
uv init --python 3.12
uv add python-dotenv langchain langchain-openai langchain-anthropic langchain-google-genai streamlit
cp .env.example .env
# Fill in your API keys in .env
streamlit run src/app.py
```

## Course

Practical Work AI — Johannes Kepler University Linz, SS 2026
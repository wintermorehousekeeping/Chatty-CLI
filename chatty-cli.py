#!/usr/bin/env python3
"""
Chatty-CLI: Enhanced Deepseek-Coder Integration with Performance Benchmarking
A coding assistant CLI tool with specialized prompts and comprehensive benchmarking
"""

import argparse
import sys
import time
import json
import csv
from pathlib import Path
from typing import Optional, Dict, List, Any
import requests
from datetime import datetime


def read_file_content(file_path: str) -> str:
    """Read and return file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


class BenchmarkLogger:
    """Handles benchmark data collection and logging"""

    def __init__(self, benchmark_dir: str = "/workspace/benchmarks"):
        self.benchmark_dir = Path(benchmark_dir)
        self.benchmark_dir.mkdir(exist_ok=True)

        # Create timestamp for this session
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.benchmark_dir / f"benchmark_{self.session_id}.json"
        self.csv_file = self.benchmark_dir / f"benchmark_{self.session_id}.csv"

        # Initialize log data
        self.log_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "benchmarks": []
        }

        # Initialize CSV writer
        self.csv_file_handle = open(self.csv_file, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file_handle)
        self.csv_writer.writerow([
            'timestamp', 'model', 'task_type', 'response_time',
            'file_size', 'prompt_length', 'response_length',
            'success', 'error_message'
        ])

    def log_benchmark(self, model: str, task_type: str, response_time: float,
                     file_size: int, prompt_length: int, response_length: int,
                     success: bool, error_message: str = ""):
        """Log a benchmark result"""

        # Log to JSON
        benchmark_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "task_type": task_type,
            "response_time": response_time,
            "file_size": file_size,
            "prompt_length": prompt_length,
            "response_length": response_length,
            "success": success,
            "error_message": error_message
        }

        self.log_data["benchmarks"].append(benchmark_entry)

        # Log to CSV
        self.csv_writer.writerow([
            benchmark_entry["timestamp"], model, task_type, response_time,
            file_size, prompt_length, response_length, success, error_message
        ])

        # Flush to disk
        self.csv_file_handle.flush()

    def close(self):
        """Close the logger and save final data"""
        try:
            self.log_data["end_time"] = datetime.now().isoformat()

            with open(self.log_file, 'w') as f:
                json.dump(self.log_data, f, indent=2)

            self.csv_file_handle.close()

            print(f"📊 Benchmark data saved to:")
            print(f"   JSON: {self.log_file}")
            print(f"   CSV: {self.csv_file}")
        except Exception as e:
            print(f"Warning: Could not save benchmark data: {e}")


class DeepseekCoderClient:
    """Enhanced client for Deepseek-Coder with specialized prompts"""

    def __init__(self, base_url: str = "http://localhost:11434", benchmark_logger: BenchmarkLogger = None):
        self.base_url = base_url
        self.benchmark_logger = benchmark_logger

    def get_specialized_prompt(self, task_type: str, context: str, question: str) -> str:
        """Generate specialized prompts based on task type"""

        task_prompts = {
            "review": f"""You are an expert code reviewer. Analyze the following code for:
- Code quality and best practices
- Potential bugs or issues
- Security vulnerabilities
- Performance improvements
- Documentation and comments

Provide specific, actionable feedback with examples where appropriate.

Code to review:
```python
{context}
```

Question: {question}""",

            "debug": f"""You are an expert debugger. The user needs help debugging this code. Analyze for:
- Logic errors and incorrect assumptions
- Runtime issues and exceptions
- Edge cases not handled
- Missing error handling
- Potential infinite loops or recursion

Provide step-by-step debugging guidance with explanations.

Code to debug:
```python
{context}
```

Question: {question}""",

            "explain": f"""You are a helpful programming teacher. Explain this code clearly and simply:
- What the code does
- How it works
- Key concepts and patterns used
- What each major section does

Use analogies or simple language when helpful.

Code to explain:
```python
{context}
```

Question: {question}""",

            "optimize": f"""You are a performance optimization expert. Analyze this code for:
- Algorithmic improvements
- Memory usage optimization
- Bottleneck identification
- Parallelization opportunities
- Python-specific optimizations

Provide concrete optimization suggestions with code examples.

Code to optimize:
```python
{context}
```

Question: {question}""",

            "general": f"""You are a helpful coding assistant. Analyze the following code:

```python
{context}
```

Question: {question}

Please provide a helpful response focusing on code analysis and improvement suggestions."""
        }

        return task_prompts.get(task_type.lower(), task_prompts["general"])

    def chat_with_benchmark(self, prompt: str, context: str, model: str = "deepseek-coder",
                           task_type: str = "general", timeout: int = 120) -> Dict[str, Any]:
        """Send a chat request to Ollama with performance tracking"""

        full_prompt = self.get_specialized_prompt(task_type, context, prompt)

        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }

        start_time = time.time()
        success = False
        response_text = ""
        error_message = ""

        try:
            # Increased timeout to 120s for first inference (model loading)
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            response_text = result.get('response', 'No response from Ollama')
            success = True

        except requests.exceptions.ConnectionError:
            error_message = "Cannot connect to Ollama. Make sure Ollama is running on http://localhost:11434"
            response_text = f"Error: {error_message}"
        except requests.exceptions.Timeout:
            error_message = f"Request to Ollama timed out (exceeded {timeout}s). Try increasing timeout with --timeout flag"
            response_text = f"Error: {error_message}"
        except requests.exceptions.HTTPError as e:
            error_message = f"Ollama returned error: {response.status_code} - {response.text}"
            response_text = f"Error: {error_message}"
        except Exception as e:
            error_message = f"Error communicating with Ollama: {e}"
            response_text = f"Error: {error_message}"

        end_time = time.time()
        response_time = end_time - start_time

        # Log benchmark data
        if self.benchmark_logger:
            self.benchmark_logger.log_benchmark(
                model=model,
                task_type=task_type,
                response_time=response_time,
                file_size=len(context.encode('utf-8')),
                prompt_length=len(full_prompt.encode('utf-8')),
                response_length=len(response_text.encode('utf-8')),
                success=success,
                error_message=error_message
            )

        return {
            "response": response_text,
            "response_time": response_time,
            "success": success,
            "error": error_message
        }

    def chat(self, prompt: str, context: str, model: str = "deepseek-coder",
            task_type: str = "general") -> str:
        """Simple chat method (backward compatibility)"""
        result = self.chat_with_benchmark(prompt, context, model, task_type)
        return result["response"]


class ModelComparator:
    """Compare performance across multiple models"""

    def __init__(self, base_url: str = "http://localhost:11434", benchmark_logger: BenchmarkLogger = None):
        self.base_url = base_url
        self.benchmark_logger = benchmark_logger
        self.client = DeepseekCoderClient(base_url, benchmark_logger)

    def compare_models(self, models: List[str], context: str, question: str,
                      task_type: str = "general", timeout: int = 120) -> Dict[str, Any]:
        """Compare responses and performance across multiple models"""

        results = {}

        for model in models:
            print(f"🧪 Testing model: {model}")

            result = self.client.chat_with_benchmark(
                prompt=question,
                context=context,
                model=model,
                task_type=task_type,
                timeout=timeout
            )

            results[model] = result

            print(f"✅ {model}: {result['response_time']:.2f}s")

        return results


def list_available_models(base_url: str = "http://localhost:11434") -> List[str]:
    """Get list of available Ollama models"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        return [model['name'] for model in data.get('models', [])]
    except Exception as e:
        print(f"Warning: Could not fetch model list: {e}")
        return ["deepseek-coder", "codellama", "llama2:7b-code"]


def main():
    parser = argparse.ArgumentParser(
        description='Chatty-CLI: Enhanced Deepseek-Coder with Performance Benchmarking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s test.py "Find bugs" --task debug
  %(prog)s main.py "Explain this code" --task explain --benchmark
  %(prog)s utils.py "Review for optimization" --task optimize --compare-model llama2:7b-code

Task Types:
  review    - Code review with quality analysis
  debug     - Debugging assistance with step-by-step guidance
  explain   - Educational explanations with teaching focus
  optimize  - Performance optimization recommendations
  general   - General code assistance (default)
        """
    )

    parser.add_argument('file', help='Python file to analyze')
    parser.add_argument('question', help='Your question about the code')
    parser.add_argument('--model', default='deepseek-coder',
                       help='Ollama model to use (default: deepseek-coder)')
    parser.add_argument('--compare-model',
                       help='Compare this model against the primary model')
    parser.add_argument('--models', nargs='+',
                       help='Compare multiple models (space-separated)')
    parser.add_argument('--task', default='general', choices=['review', 'debug', 'explain', 'optimize', 'general'],
                       help='Task type for specialized prompting (default: general)')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                       help='Ollama API URL (default: http://localhost:11434)')
    parser.add_argument('--timeout', type=int, default=120,
                       help='Request timeout in seconds (default: 120 for first run, increase if needed)')
    parser.add_argument('--benchmark', action='store_true',
                       help='Enable performance benchmarking')
    parser.add_argument('--list-models', action='store_true',
                       help='List available Ollama models and exit')

    args = parser.parse_args()

    # List models and exit
    if args.list_models:
        print("Available Ollama models:")
        models = list_available_models(args.ollama_url)
        for model in models:
            print(f"  - {model}")
        return

    # Validate file exists
    if not Path(args.file).exists():
        print(f"Error: File '{args.file}' does not exist")
        sys.exit(1)

    # Read file content
    print(f"📖 Reading file: {args.file}")
    file_content = read_file_content(args.file)
    file_size = len(file_content.encode('utf-8'))
    print(f"📊 File size: {file_size:,} bytes")

    # Initialize benchmark logger
    benchmark_logger = BenchmarkLogger() if args.benchmark else None

    # Initialize client
    client = DeepseekCoderClient(base_url=args.ollama_url, benchmark_logger=benchmark_logger)

    print(f"❓ Asking: {args.question}")
    print(f"🤖 Using task type: {args.task}")
    print(f"⏱️  Timeout: {args.timeout}s (first inference may take 30-60s)")

    if args.models:
        print(f"🔬 Comparing models: {', '.join(args.models)}")
        print("\n" + "="*80 + "\n")

        # Model comparison mode
        comparator = ModelComparator(args.ollama_url, benchmark_logger)
        results = comparator.compare_models(args.models, file_content, args.question, args.task, args.timeout)

        # Display results
        print("\n📊 COMPARISON RESULTS:")
        print("="*80)

        for model, result in results.items():
            print(f"\n🤖 Model: {model}")
            print(f"⏱️  Response time: {result['response_time']:.2f}s")
            print(f"✅ Success: {result['success']}")
            print("="*40)
            print(result['response'])
            print("="*80)

    elif args.compare_model:
        print(f"🔬 Comparing: {args.model} vs {args.compare_model}")
        print("\n" + "="*80 + "\n")

        # Two-model comparison
        models = [args.model, args.compare_model]
        comparator = ModelComparator(args.ollama_url, benchmark_logger)
        results = comparator.compare_models(models, file_content, args.question, args.task, args.timeout)

        # Display results
        print("\n📊 COMPARISON RESULTS:")
        print("="*80)

        for model, result in results.items():
            print(f"\n🤖 Model: {model}")
            print(f"⏱️  Response time: {result['response_time']:.2f}s")
            print(f"✅ Success: {result['success']}")
            print("="*40)
            print(result['response'])
            print("="*80)

    else:
        # Single model mode
        print(f"🤖 Using model: {args.model}")
        print("\n" + "="*80 + "\n")

        result = client.chat_with_benchmark(
            prompt=args.question,
            context=file_content,
            model=args.model,
            task_type=args.task,
            timeout=args.timeout
        )

        if result['success']:
            print(f"⏱️  Response time: {result['response_time']:.2f}s")
            print(f"✅ Model: {args.model} ({args.task} task)")
        else:
            print(f"❌ Error: {result['error']}")

        print("\n" + "="*40 + "\n")
        print(result['response'])
        print("\n" + "="*80)

    # Close benchmark logger
    if benchmark_logger:
        benchmark_logger.close()


if __name__ == "__main__":
    main()

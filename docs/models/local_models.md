# Local Language Models

Peen-SWE supports local models via any OpenAI-compatible HTTP inference engine, including [Ollama](https://ollama.com/), [vLLM](https://docs.vllm.ai/), and [LM Studio](https://lmstudio.ai/).

Running locally requires no paid API tokens and keeps all source code, shell interactions, and execution logs completely offline.

---

## 1. Quickstart: Ollama

[Ollama](https://ollama.com/) provides the fastest way to run code models locally.

### Step 1: Pull a Coding Model
We recommend the [Qwen 2.5 Coder](https://ollama.com/library/qwen2.5-coder) family:

```bash
ollama run qwen2.5-coder:7b
# Or for larger GPU rigs:
# ollama run qwen2.5-coder:14b
# ollama run qwen2.5-coder:32b
```

### Step 2: Bypass Cost Tracking
Local models are not in LiteLLM's public pricing catalog. Disable cost calculation errors:

```bash
export MSWEA_COST_TRACKING="ignore_errors"
```

### Step 3: Launch Peen-SWE
Specify the `ollama/` prefix:

```bash
peen -m "ollama/qwen2.5-coder:7b"
```

Ollama automatically exposes its OpenAI-compatible endpoint at `http://localhost:11434`.

---

## 2. High-Throughput Inference: vLLM

For parallel evaluation, batch SWE-bench runs, or multi-GPU environments, [vLLM](https://docs.vllm.ai/) offers state-of-the-art throughput and PagedAttention.

### Step 1: Launch the vLLM Server

```bash
vllm serve Qwen/Qwen2.5-Coder-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 32768
```

### Step 2: Configure Peen-SWE

Invoke Peen-SWE pointing to the local vLLM endpoint:

```bash
peen -m "openai/Qwen/Qwen2.5-Coder-7B-Instruct" \
    --model-kwargs '{"api_base": "http://localhost:8000/v1", "api_key": "dummy"}'
```

Or configure via `peen.yaml`:

```yaml
model:
  model_name: "openai/Qwen/Qwen2.5-Coder-7B-Instruct"
  cost_tracking: "ignore_errors"
  model_kwargs:
    api_base: "http://localhost:8000/v1"
    api_key: "dummy"
```

---

## 3. Desktop Inference: LM Studio

1. Open **LM Studio** and download a model (e.g. `Qwen2.5-Coder-7B-Instruct-GGUF`).
2. Navigate to the **Developer / Local Server** tab (`<->`).
3. Start the server (default: `http://localhost:1234/v1`).
4. Run Peen-SWE:

```bash
export MSWEA_COST_TRACKING="ignore_errors"
peen -m "openai/local-model" \
    --model-kwargs '{"api_base": "http://localhost:1234/v1", "api_key": "dummy"}'
```

---

## 4. Custom Token & Cost Registry

If you want accurate token tracking without ignoring errors, create a `registry.json` mapping your local model identifier:

```json
{
  "qwen2.5-coder:7b": {
    "max_tokens": 32768,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "litellm_provider": "ollama",
    "mode": "chat"
  },
  "Qwen/Qwen2.5-Coder-7B-Instruct": {
    "max_tokens": 32768,
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "litellm_provider": "openai",
    "mode": "chat"
  }
}
```

Tell Peen-SWE to load this registry:

```bash
export LITELLM_MODEL_REGISTRY_PATH="/path/to/registry.json"
# Or save to your global config:
peen-extra config set LITELLM_MODEL_REGISTRY_PATH "/path/to/registry.json"
```

---

## 5. Benchmarking Local Models with SWE-bench

To benchmark a local model against SWE-bench tasks:

```bash
export MSWEA_COST_TRACKING="ignore_errors"

peen-swebench \
    --model "openai/Qwen/Qwen2.5-Coder-7B-Instruct" \
    --subset verified \
    --split test \
    --filter '^(django__django-11099)$' \
    --output ./local_bench_results
```

{% include-markdown "../_footer.md" %}

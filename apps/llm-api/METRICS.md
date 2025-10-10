# Performance Metrics & Evaluation Guide

This guide explains the performance metrics provided by the LLM API and how to interpret them for evaluating and optimizing your LLM deployment.

## Overview

The API automatically tracks and returns comprehensive performance metrics following industry best practices from NVIDIA, Databricks, and other LLM benchmarking standards.

## Metrics Reference

### 1. Time to First Token (TTFT)

**Definition**: The time elapsed from sending a request until receiving the first token.

**Unit**: Seconds

**Available In**: Streaming endpoints only

**Interpretation**:
- **< 0.3s**: Excellent - Ideal for real-time chatbots
- **0.3-0.5s**: Good - Acceptable for most interactive applications
- **0.5-1.0s**: Fair - May feel slightly sluggish
- **> 1.0s**: Poor - Users will notice delays

**Use Cases**:
- Real-time chat applications
- Interactive assistants
- Live customer support

**Optimization Tips**:
- Reduce prompt length
- Use smaller models for initial responses
- Implement prompt caching
- Optimize GPU memory bandwidth

### 2. Total Latency (E2EL)

**Definition**: End-to-end latency from request submission to receiving the final token.

**Unit**: Seconds

**Available In**: Both streaming and non-streaming

**Interpretation**:
- **< 2s**: Excellent for short responses
- **2-5s**: Good for medium responses
- **5-10s**: Acceptable for long-form content
- **> 10s**: Consider streaming or async processing

**Factors Affecting Total Latency**:
- Prompt length (input tokens)
- Response length (output tokens)
- Model size
- Server load
- Network latency

### 3. Tokens Per Second (TPS)

**Definition**: Overall throughput calculated as (input tokens + output tokens) / total latency.

**Unit**: tokens/second

**Available In**: Both streaming and non-streaming

**Interpretation**:
- **> 100**: Excellent throughput
- **50-100**: Good performance
- **25-50**: Acceptable for most use cases
- **< 25**: May need optimization

**Note**: This metric includes both prompt processing and generation time.

### 4. Output Tokens Per Second

**Definition**: Generation speed calculated as output tokens / generation time (excluding prompt processing).

**Unit**: tokens/second

**Available In**: Both streaming and non-streaming

**Interpretation**:
- **> 80**: Excellent - Faster than human reading speed
- **50-80**: Good - Comfortable streaming experience
- **30-50**: Acceptable - Slight delays may be noticeable
- **< 30**: Slow - Consider model optimization

**Use Cases**:
- Measuring pure generation performance
- Comparing different models
- Optimizing for streaming applications

### 5. Time Per Output Token (TPOT)

**Definition**: Average time between generating consecutive tokens (generation time / output tokens).

**Unit**: Seconds

**Available In**: Both streaming and non-streaming

**Interpretation**:
- **< 0.015s**: Excellent - Smooth streaming
- **0.015-0.025s**: Good - Comfortable pace
- **0.025-0.040s**: Fair - Slightly choppy
- **> 0.040s**: Poor - Noticeable delays

**Relationship to Reading Speed**:
- Average human reading: ~250 words/min = ~4 words/sec
- 1 token ≈ 0.75 words
- Target TPOT: < 0.020s for smooth experience

### 6. Input Tokens

**Definition**: Number of tokens in the input prompt (including system messages).

**Unit**: Count

**Available In**: Both streaming and non-streaming

**Use Cases**:
- Cost estimation (many LLM APIs charge per token)
- Understanding prompt complexity
- Optimizing prompt templates

**Optimization**:
- Remove unnecessary context
- Use concise system prompts
- Implement context windowing for long conversations

### 7. Output Tokens

**Definition**: Number of tokens generated in the response.

**Unit**: Count

**Available In**: Both streaming and non-streaming

**Use Cases**:
- Cost tracking
- Response length analysis
- Setting appropriate max_tokens limits

**Control Methods**:
- Set `max_tokens` parameter
- Use stop sequences
- Prompt engineering for concise responses

## Benchmarking Best Practices

### 1. Test with Realistic Data

```python
# Example: Benchmark with actual use case prompts
test_prompts = [
    {"role": "user", "content": "Short question"},
    {"role": "user", "content": "Medium length query with more context..."},
    {"role": "user", "content": "Long detailed request with multiple requirements..."}
]

for prompt in test_prompts:
    response = requests.post("http://localhost:8000/v1/chat", json={
        "messages": [prompt],
        "temperature": 0.2
    })
    metrics = response.json()["metrics"]
    print(f"Prompt length: {metrics['input_tokens']} tokens")
    print(f"TPOT: {metrics['tpot']}s")
    print(f"Output TPS: {metrics['output_tokens_per_second']}")
```

### 2. Measure Under Different Loads

- Test single requests (best-case latency)
- Test concurrent requests (throughput under load)
- Test sustained load (stability over time)

### 3. Compare Across Configurations

Track metrics when changing:
- Model size (e.g., 1.7B vs 7B parameters)
- Temperature settings
- Max token limits
- Hardware (CPU vs GPU)

### 4. Monitor Trends Over Time

```python
# Log metrics for analysis
import csv
import datetime

def log_metrics(metrics, prompt_category):
    with open('metrics_log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.datetime.now().isoformat(),
            prompt_category,
            metrics['total_latency'],
            metrics['ttft'],
            metrics['output_tokens_per_second'],
            metrics['input_tokens'],
            metrics['output_tokens']
        ])
```

## Performance Optimization Guide

### For Low Latency (Minimize TTFT)

1. **Use smaller models** - Faster prompt processing
2. **Implement KV cache** - Reuse computed attention states
3. **Optimize prompt length** - Shorter prompts = faster TTFT
4. **GPU memory management** - Ensure sufficient VRAM

### For High Throughput (Maximize TPS)

1. **Batch requests** - Process multiple requests together
2. **Use larger models** - Better parallelization
3. **Optimize batch size** - Find sweet spot for your hardware
4. **Enable quantization** - Trade precision for speed

### For Smooth Streaming (Optimize TPOT)

1. **Target TPOT < 0.020s** - Faster than reading speed
2. **Monitor GPU utilization** - Ensure full utilization
3. **Reduce memory bottlenecks** - Optimize KV cache
4. **Use continuous batching** - Better GPU utilization

## Common Metrics Questions

### Why is my TTFT high but TPOT low?

- Large prompt requires significant processing time
- Once generation starts, it's fast
- **Solution**: Implement prompt caching or use smaller context

### Why do I see NULL values for some metrics?

- **TTFT**: Only available in streaming mode
- **Token counts**: Depends on Ollama response data
- **TPOT**: Only calculated if output tokens > 0

### How do metrics compare to ChatGPT?

Typical ChatGPT metrics:
- TTFT: 0.2-0.5s
- Output TPS: 50-80 tokens/second
- TPOT: 0.012-0.020s

Your local model may vary based on hardware.

### Should I optimize for TTFT or TPOT?

Depends on use case:
- **Chat applications**: Prioritize TTFT (responsiveness)
- **Content generation**: Prioritize output TPS (throughput)
- **Streaming UI**: Prioritize TPOT (smoothness)

## Monitoring & Alerting

### Set Up Alerts

```python
def check_performance(metrics):
    alerts = []
    
    if metrics.get('ttft') and metrics['ttft'] > 1.0:
        alerts.append("High TTFT: User experience degraded")
    
    if metrics.get('output_tokens_per_second', 0) < 30:
        alerts.append("Low output TPS: Generation too slow")
    
    if metrics.get('total_latency') > 10.0:
        alerts.append("High total latency: Consider async processing")
    
    return alerts
```

### Dashboard Metrics

Track these KPIs:
- **P50, P90, P99 latencies** - Understand tail performance
- **Average TTFT** - Monitor responsiveness trend
- **Average output TPS** - Track generation speed
- **Error rate** - Ensure reliability

## References

- [NVIDIA NIM LLM Benchmarking Metrics](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html)
- [Databricks LLM Inference Performance](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
- [BentoML LLM Inference Metrics](https://bentoml.com/llm/inference-optimization/llm-inference-metrics)

## Contributing

Found a way to improve performance metrics? Please contribute!

1. Test your optimization
2. Measure before/after metrics
3. Document your findings
4. Submit a PR with improvements

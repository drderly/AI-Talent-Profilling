"""
Test script for ONNX GenAI backend
Demonstrates both streaming and non-streaming endpoints with metrics
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8002"

print("=" * 60)
print("ONNX GenAI Backend Test")
print("=" * 60)

# Test 1: Health Check
print("\n1. Health Check")
print("-" * 60)
response = requests.get(f"{BASE_URL}/healthz")
print(json.dumps(response.json(), indent=2))

# Test 2: Non-Streaming Chat
print("\n2. Non-Streaming Chat")
print("-" * 60)

request_data = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is ONNX Runtime GenAI in one sentence?"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

print(f"Request: {json.dumps(request_data, indent=2)}\n")

response = requests.post(
    f"{BASE_URL}/v1/chat",
    json=request_data,
    timeout=60
)

if response.status_code == 200:
    result = response.json()
    print("✓ Response received:")
    print(result["content"])
    
    # Display performance metrics
    print("\n📊 Performance Metrics:")
    metrics = result.get("metrics", {})
    print(f"  - Total Latency: {metrics.get('total_latency')}s")
    print(f"  - Tokens/Second: {metrics.get('tokens_per_second')}")
    print(f"  - Output Tokens/Second: {metrics.get('output_tokens_per_second')}")
    print(f"  - Input Tokens: {metrics.get('input_tokens')}")
    print(f"  - Output Tokens: {metrics.get('output_tokens')}")
    print(f"  - TPOT (Time Per Output Token): {metrics.get('tpot')}s")
    print(f"  - Model: {metrics.get('model')}")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)

# Test 3: Streaming Chat
print("\n3. Streaming Chat")
print("-" * 60)

stream_request = {
    "messages": [
        {"role": "user", "content": "Count from 1 to 5"}
    ],
    "temperature": 0.2,
    "max_tokens": 50
}

print(f"Request: {json.dumps(stream_request, indent=2)}\n")

response_stream = requests.post(
    f"{BASE_URL}/v1/chat/stream",
    json=stream_request,
    stream=True,
    timeout=60
)

if response_stream.status_code == 200:
    print("✓ Streaming response:")
    for line in response_stream.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                if data.get('done'):
                    print("\n\n[Stream completed]")
                    
                    # Display metrics from streaming
                    if 'metrics' in data:
                        print("\n📊 Streaming Performance Metrics:")
                        metrics = data['metrics']
                        print(f"  - TTFT (Time to First Token): {metrics.get('ttft')}s")
                        print(f"  - Total Latency: {metrics.get('total_latency')}s")
                        print(f"  - Tokens/Second: {metrics.get('tokens_per_second')}")
                        print(f"  - Output Tokens/Second: {metrics.get('output_tokens_per_second')}")
                        print(f"  - Input Tokens: {metrics.get('input_tokens')}")
                        print(f"  - Output Tokens: {metrics.get('output_tokens')}")
                        print(f"  - TPOT (Time Per Output Token): {metrics.get('tpot')}s")
                        print(f"  - Model: {metrics.get('model')}")
                    break
                print(data.get('token', ''), end='', flush=True)
else:
    print(f"✗ Error: {response_stream.status_code}")
    print(response_stream.text)

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)

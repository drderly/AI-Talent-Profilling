"""
Example script to send complex prompts with JSON structure to the LLM API
"""
import requests
import json

# Your complex prompt with JSON structure
prompt = """Task: Compare the semantic similarity of the following ten keywords against the Target Concept: Sustainable E-commerce for the German (de-DE) market.

Target Concept (English): Sustainable E-commerce

List of Keywords (English/German Mix) to Compare:
1. Green shipping
2. Klimaneutrale Lieferung
3. Circular economy
4. Fair trade
5. Lokal produziert
6. Transparente Lieferkette
7. Emissionsarme Logistik
8. Gebrauchtware
9. Nachhaltigkeitssiegel
10. Ökostrom-Betrieb

You MUST return your response as a single JSON object (with no other text or explanation) that adheres exactly to the structure defined below.

Assess the similarity on a scale of 0 to 5 (0 = No similarity, 5 = Essential component).

Required JSON Output Structure:
{
  "target_concept": "Sustainable E-commerce",
  "locale": "de-DE",
  "similarity_ratings": [
    { "keyword": "Green shipping", "similarity_score": [0-5] },
    { "keyword": "Klimaneutrale Lieferung", "similarity_score": [0-5] },
    { "keyword": "Circular economy", "similarity_score": [0-5] },
    { "keyword": "Fair trade", "similarity_score": [0-5] },
    { "keyword": "Lokal produziert", "similarity_score": [0-5] },
    { "keyword": "Transparente Lieferkette", "similarity_score": [0-5] },
    { "keyword": "Emissionsarme Logistik", "similarity_score": [0-5] },
    { "keyword": "Gebrauchtware", "similarity_score": [0-5] },
    { "keyword": "Nachhaltigkeitssiegel", "similarity_score": [0-5] },
    { "keyword": "Ökostrom-Betrieb", "similarity_score": [0-5] }
  ]
}"""

# Prepare the request
request_data = {
    "model": "smollm2:1.7b",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant that analyzes semantic similarity and returns structured JSON responses."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    "temperature": 0.2,
    "max_tokens": 2000
}

# Send non-streaming request
print("Sending request to LLM API...")
response = requests.post(
    "http://127.0.0.1:8000/v1/chat",
    json=request_data,
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    print("\n✓ Response received:")
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
    
    # Try to parse the LLM's response as JSON
    try:
        llm_json = json.loads(result["content"])
        print("\n✓ Valid JSON response from LLM:")
        print(json.dumps(llm_json, indent=2))
    except json.JSONDecodeError:
        print("\n⚠ LLM response is not valid JSON")
else:
    print(f"\n✗ Error: {response.status_code}")
    print(response.text)

# Example with streaming
print("\n" + "="*60)
print("Streaming example:")
print("="*60)

response_stream = requests.post(
    "http://127.0.0.1:8000/v1/chat/stream",
    json=request_data,
    stream=True,
    timeout=120
)

if response_stream.status_code == 200:
    print("\n✓ Streaming response:")
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
    print(f"\n✗ Error: {response_stream.status_code}")
    print(response_stream.text)

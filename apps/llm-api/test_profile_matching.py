"""
Test script for employee profile matching using the LLM API.
Sends the profile matching prompt and displays the results.
"""
import requests
import json

# API Configuration
API_URL = "http://localhost:8002/v1/chat"
# For streaming: API_URL = "http://localhost:8002/v1/chat/stream"

# Load the request prompt
with open("request_prompt.json", "r", encoding="utf-8") as f:
    request_data = json.load(f)

print("=" * 80)
print("EMPLOYEE PROFILE MATCHING TEST")
print("=" * 80)
print(f"\nSending request to: {API_URL}")
print(f"Model: {request_data['model']}")
print(f"Temperature: {request_data['temperature']}")
print(f"Max Tokens: {request_data['max_tokens']}")
print(f"\nPrompt length: {len(request_data['messages'][1]['content'])} characters")
print("\n" + "=" * 80)
print("Waiting for response...\n")

try:
    # Send request
    response = requests.post(API_URL, json=request_data, timeout=300)
    response.raise_for_status()
    
    # Parse response
    result = response.json()
    
    print("=" * 80)
    print("RESPONSE RECEIVED")
    print("=" * 80)
    
    # Display content
    content = result.get("content", "")
    print(f"\nGenerated Content:\n{content}\n")
    
    # Try to parse the content as JSON for better display
    try:
        profile_result = json.loads(content)
        print("=" * 80)
        print("PARSED PROFILE MATCHING RESULT")
        print("=" * 80)
        print(f"\nProfile Similarity Score: {profile_result.get('PROFILE_SIMILARITY', 'N/A')}")
        print(f"\nProfile Summary:\n{profile_result.get('PROFILE_SUMMARY', 'N/A')}\n")
    except json.JSONDecodeError:
        print("Note: Response is not valid JSON. Raw content displayed above.")
    
    # Display metrics
    if "metrics" in result:
        metrics = result["metrics"]
        print("=" * 80)
        print("PERFORMANCE METRICS")
        print("=" * 80)
        print(f"Total Latency: {metrics.get('total_latency', 'N/A')}s")
        print(f"TTFT (Time to First Token): {metrics.get('ttft', 'N/A')}s")
        print(f"Input Tokens: {metrics.get('input_tokens', 'N/A')}")
        print(f"Output Tokens: {metrics.get('output_tokens', 'N/A')}")
        print(f"Tokens/Second: {metrics.get('tokens_per_second', 'N/A')}")
        print(f"Output Tokens/Second: {metrics.get('output_tokens_per_second', 'N/A')}")
        print(f"TPOT (Time Per Output Token): {metrics.get('tpot', 'N/A')}s")
        print(f"Model: {metrics.get('model', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)

except requests.exceptions.Timeout:
    print("ERROR: Request timed out. The model may be taking too long to respond.")
except requests.exceptions.ConnectionError:
    print(f"ERROR: Could not connect to {API_URL}. Is the server running?")
except requests.exceptions.HTTPError as e:
    print(f"ERROR: HTTP {e.response.status_code}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

import sys
import httpx

MODEL = sys.argv[1] if len(sys.argv) > 1 else "llama3.1:8b"
BASE = "http://localhost:11434"

def main() -> int:
    try:
        v = httpx.get(f"{BASE}/api/version", timeout=5).json()
    except Exception as e:
        print(f"FAIL: Ollama not reachable at {BASE}: {e}")
        return 1
    print(f"OK: Ollama version {v.get('version')}")
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Reply with exactly: PONG"}],
        "stream": False,
    }
    try:
        r = httpx.post(f"{BASE}/api/chat", json=payload, timeout=120)
        r.raise_for_status()
    except Exception as e:
        print(f"FAIL: chat request failed: {e}")
        return 1
    print(f"OK: {MODEL} replied: {r.json()['message']['content']!r}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

"""Mock bridge for testing integration."""
import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str)
    args, _ = parser.parse_known_args()

    # Simulate delay
    # time.sleep(0.5)

    response = {
        "result": "The Roman Empire was one of the largest empires in history...",
        "messages_total": 5,
        "mock": True
    }
    
    sys.stdout.write(json.dumps(response))
    sys.exit(0)

if __name__ == "__main__":
    main()

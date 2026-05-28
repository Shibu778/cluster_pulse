import sys
from src.config_loader import load_config
from src.scheduler import start_scheduler

def main():
    try:
        # Load up configuration attributes automatically using directory fallback logic
        config = load_config()
        
        # Start the background polling engine
        start_scheduler(config)
        
    except Exception as e:
        print(f"🚨 Critical Failure initialization: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
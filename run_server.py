import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server.main import Server

def main():
    parser = argparse.ArgumentParser(description='Start the game server')
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8765, help='Server port (default: 8765)')
    
    args = parser.parse_args()
    
    print("Starting Game Server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    
    server = Server(host=args.host, port=args.port)
    
    try:
        server.receive()
    except KeyboardInterrupt:
        print("Server interrupted by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
    finally:
        server.server.close()
        print("Server stopped")

if __name__ == "__main__":
    main() 
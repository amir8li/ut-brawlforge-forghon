import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server.main import Server

def main():
    parser = argparse.ArgumentParser(description='Start the game server')
    
    # Use environment variables for Docker deployment, with fallbacks
    default_host = os.getenv('SERVER_HOST', '0.0.0.0')
    default_port = int(os.getenv('SERVER_PORT', '8765'))
    
    parser.add_argument('--host', default=default_host, help=f'Server host (default: {default_host})')
    parser.add_argument('--port', type=int, default=default_port, help=f'Server port (default: {default_port})')
    
    args = parser.parse_args()
    
    print("Starting Game Server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    
    print("[MAIN] Creating server instance...")
    server = Server(host=args.host, port=args.port)
    print("[MAIN] Server instance created successfully")
    
    try:
        print("[MAIN] Starting server.receive()...")
        server.receive()
    except KeyboardInterrupt:
        print("Server interrupted by user")
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        server.server.close()
        print("Server stopped")

if __name__ == "__main__":
    main() 
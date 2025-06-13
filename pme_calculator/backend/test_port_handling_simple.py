def main():
    """Start the FastAPI server with intelligent port handling."""
    preferred_port = get_port_config()
    start_server_with_fallback(preferred_port)

if __name__ == "__main__":
    main() 
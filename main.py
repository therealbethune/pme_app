#!/usr/bin/env python3
"""
Fund Analysis Tool Application
Main entry point for launching the web-based PME calculation tool.
"""
import subprocess
from pathlib import Path

import structlog

logger = structlog.get_logger()


def main() -> int:
    """Finds and executes the start_app.sh script."""
    logger.info("Launching Fund Analysis Tool Web Application...")

    # The script should be in the same directory as this main.py
    script_path = Path(__file__).parent / "start_app.sh"

    if not script_path.is_file():
        logger.error(f"Error: start_app.sh not found at {script_path}")
        logger.error("Please ensure start_app.sh is in the project root directory.")
        return 1

    try:
        # Make sure the script is executable
        script_path.chmod(0o755)

        # Run the script and stream its output
        process = subprocess.Popen(
            ["bash", str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Print output line-by-line
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                print(line.strip())

        # Wait for the process to complete
        return_code = process.wait()

        if return_code != 0:
            logger.error(f"Script exited with code {return_code}.")

        return return_code

    except FileNotFoundError:
        logger.error(
            "Error: 'bash' command not found. Please ensure bash is installed and in your PATH."
        )
        return 1
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    if exit_code == 0:
        logger.info("Application shut down gracefully.")
    else:
        logger.error("Application shut down with errors.")
    exit(exit_code)

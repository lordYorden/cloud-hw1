#!/usr/bin/env python3
"""
Cross-platform setup script for cloud-hw1 project.
Installs dependencies, starts Docker, runs migrations, and launches the server.
"""

import os
import sys
import subprocess
import socket
import shutil
import time

# Enable ANSI colors on Windows
if sys.platform == "win32":
    os.system("color")

# ANSI color codes
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BLUE = "\033[34m"


def print_success(msg: str) -> None:
    """Print success message in green."""
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg: str) -> None:
    """Print error message in red."""
    print(f"{RED}✗ {msg}{RESET}")


def print_warning(msg: str) -> None:
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠ {msg}{RESET}")


def print_info(msg: str) -> None:
    """Print info message in blue."""
    print(f"{BLUE}→ {msg}{RESET}")


def run_command(args: list, description: str) -> bool:
    """Run a command and return True if successful."""
    print_info(f"{description}...")
    result = subprocess.run(args, capture_output=False)
    if result.returncode == 0:
        print_success(description)
        return True
    else:
        print_error(f"{description} failed (exit code: {result.returncode})")
        return False


def check_env_file() -> bool:
    """Check if .env file exists."""
    if os.path.exists(".env"):
        print_success(".env file found")
        return True
    else:
        print_error(".env file not found!")
        print_warning("Please create a .env file from .env.example and fill in the required values.")
        return False


def install_dependencies() -> bool:
    """Install Python dependencies using pip."""
    return run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing Python dependencies"
    )


def get_docker_compose_command() -> list:
    """Get the appropriate docker-compose command for the system."""
    # Try docker-compose first (older Docker installations)
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    # Try docker compose (newer Docker Desktop)
    if shutil.which("docker"):
        # Check if 'docker compose' subcommand works
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return ["docker", "compose"]
    return []


def wait_for_postgres(host: str = "localhost", port: int = 5432, max_attempts: int = 30) -> bool:
    """Wait for PostgreSQL to be ready by checking if the port is open."""
    print_info("Waiting for PostgreSQL to be ready...")
    for attempt in range(max_attempts):
        try:
            with socket.create_connection((host, port), timeout=1):
                print_success("PostgreSQL is ready")
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            print(f"{YELLOW}.{RESET}", end="", flush=True)
            time.sleep(1)
    print()  # New line after dots
    print_error(f"PostgreSQL not ready after {max_attempts} seconds")
    return False


def start_docker() -> bool:
    """Start Docker containers."""
    docker_cmd = get_docker_compose_command()
    if docker_cmd is None:
        print_error("docker-compose or docker compose not found. Please install Docker.")
        return False

    # Stop existing containers for clean state
    print_info("Stopping existing containers...")
    subprocess.run(docker_cmd + ["down"], capture_output=True)

    # Start containers
    if not run_command(docker_cmd + ["up", "-d"], "Starting Docker containers"):
        return False

    # Wait for PostgreSQL to be ready
    return wait_for_postgres()


def run_migrations() -> bool:
    """Run Alembic database migrations."""
    return run_command(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        "Running database migrations"
    )


def start_server() -> None:
    """Start the uvicorn server in foreground."""
    print()
    print_info("Starting uvicorn server...")
    print_info("Visit http://localhost:8000/ to initialize data")
    print_info("Visit http://localhost:8000/docs for swagger UI")
    print()
    
    # Run uvicorn in foreground (blocking)
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "localhost",
        "--port", "8000"
    ])


def main() -> int:
    """Main setup function."""
    print()
    print(f"{GREEN}{'='*50}{RESET}")
    print(f"{GREEN}  Cloud HW1 - Project Setup Script{RESET}")
    print(f"{GREEN}{'='*50}{RESET}")
    print()

    # Change to script directory (project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print_info(f"Working directory: {script_dir}")
    print()

    # Step 1: Check .env file
    if not check_env_file():
        return 1

    # Step 2: Install dependencies
    if not install_dependencies():
        return 1

    # Step 3: Start Docker
    if not start_docker():
        return 1

    # Step 4: Run migrations
    if not run_migrations():
        return 1

    # Step 5: Start server
    print()
    print_success("Setup completed successfully!")
    start_server()

    return 0


if __name__ == "__main__":
    sys.exit(main())

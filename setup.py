"""
Setup and Installation Script for CBT Chatbot

This script helps with initial setup and verification.
"""
import os
import sys
from pathlib import Path
import subprocess


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {text} ".center(70))
    print("="*70 + "\n")


def print_step(step, text):
    """Print step information"""
    print(f"\n[{step}] {text}")


def check_python_version():
    """Check Python version"""
    print_step("1", "Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} is not supported")
        print("  Please install Python 3.8 or higher")
        return False


def check_env_file():
    """Check if .env file exists"""
    print_step("2", "Checking environment configuration...")
    if Path(".env").exists():
        print("✓ .env file found")
        return True
    else:
        print("⚠ .env file not found")
        print("  Creating from .env.example...")
        try:
            with open(".env.example", "r") as src:
                content = src.read()
            with open(".env", "w") as dst:
                dst.write(content)
            print("✓ Created .env file")
            print("\n⚠ IMPORTANT: Edit .env and add your OPENAI_API_KEY")
            return False
        except Exception as e:
            print(f"✗ Error creating .env: {e}")
            return False


def install_dependencies():
    """Install Python dependencies"""
    print_step("3", "Installing dependencies...")
    print("This may take a few minutes...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        print("\nTry manually:")
        print("  pip install -r requirements.txt")
        return False


def create_directories():
    """Create necessary directories"""
    print_step("4", "Creating directories...")
    directories = [
        "data/raw",
        "data/processed",
        "data/models",
        "logs"
    ]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✓ Directories created")
    return True


def verify_openai_key():
    """Verify OpenAI API key is set"""
    print_step("5", "Verifying OpenAI API key...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            print("✓ OpenAI API key configured")
            return True
        else:
            print("⚠ OpenAI API key not configured")
            print("\nPlease edit .env and add your key:")
            print("  OPENAI_API_KEY=sk-your-key-here")
            return False
    except Exception as e:
        print(f"⚠ Could not verify API key: {e}")
        return False


def run_tests():
    """Run system tests"""
    print_step("6", "Running system tests...")
    print("This will test basic functionality (without training)...")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/test_system.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✓ System tests passed")
            return True
        else:
            print("⚠ Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"⚠ Could not run tests: {e}")
        return False


def print_next_steps(api_key_configured):
    """Print next steps"""
    print_header("Setup Complete!")
    
    print("Next Steps:\n")
    
    if not api_key_configured:
        print("1. ⚠ IMPORTANT: Configure your OpenAI API key")
        print("   Edit .env and add: OPENAI_API_KEY=sk-your-key-here\n")
    
    print("2. Train the CBT model (first time only):")
    print("   python scripts\\train_model.py")
    print("   (This takes 30-60 minutes)\n")
    
    print("3. Run the chatbot:")
    print("   Option A - Console: python console_chat.py")
    print("   Option B - API Server: python main.py\n")
    
    print("4. Read the documentation:")
    print("   - QUICKSTART.md - Quick start guide")
    print("   - TECHNICAL_DOCS.md - Technical documentation")
    print("   - README.md - Project overview\n")
    
    print("For API documentation (after starting server):")
    print("   http://localhost:8000/docs\n")
    
    print("="*70)


def main():
    """Main setup function"""
    print_header("CBT Chatbot Setup")
    
    print("This script will help you set up the CBT chatbot system.")
    print("It will:")
    print("  1. Check Python version")
    print("  2. Create environment configuration")
    print("  3. Install dependencies")
    print("  4. Create necessary directories")
    print("  5. Verify configuration")
    print("  6. Run basic tests")
    
    input("\nPress Enter to continue...")
    
    # Run setup steps
    steps_passed = []
    
    steps_passed.append(check_python_version())
    api_key_configured = check_env_file()
    steps_passed.append(True)  # env file step always continues
    
    steps_passed.append(install_dependencies())
    steps_passed.append(create_directories())
    steps_passed.append(verify_openai_key())
    
    # Only run tests if basic setup passed
    if all(steps_passed[:4]):
        steps_passed.append(run_tests())
    
    # Print next steps
    print_next_steps(api_key_configured)
    
    if all(steps_passed):
        print("\n✓ Setup completed successfully!")
    else:
        print("\n⚠ Setup completed with warnings")
        print("  Please address the issues above before continuing")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Setup failed: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Setup script for SwiftQueue Hospital
This script helps set up the development environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ {command}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_node_version():
    """Check if Node.js version is compatible"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js is not installed or not in PATH")
    return False

def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    venv_path = backend_dir / "venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        result = run_command("python -m venv venv", cwd=backend_dir)
        if not result:
            return False
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_command = venv_path / "Scripts" / "pip"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_command = venv_path / "bin" / "pip"
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    result = run_command(f"{pip_command} install -r requirements.txt", cwd=backend_dir)
    if not result:
        return False
    
    # Initialize database
    print("Initializing database...")
    result = run_command(f"{pip_command} run init_db.py", cwd=backend_dir)
    if not result:
        return False
    
    print("✅ Backend setup complete")
    return True

def setup_frontend():
    """Set up the frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    # Install Node.js dependencies
    print("Installing Node.js dependencies...")
    result = run_command("npm install")
    if not result:
        return False
    
    print("✅ Frontend setup complete")
    return True

def create_env_file():
    """Create environment configuration file"""
    print("\n🔧 Creating environment configuration...")
    
    env_content = """# Environment Configuration for SwiftQueue Hospital
ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DATABASE_URL=sqlite:///./queue_management.db
"""
    
    env_file = Path("backend") / ".env"
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")
    
    return True

def main():
    """Main setup function"""
    print("🏥 SwiftQueue Hospital Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    # Set up backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Set up frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("❌ Environment configuration failed")
        sys.exit(1)
    
    print("\n🎉 Setup complete!")
    print("\nTo start the application:")
    print("1. Backend: cd backend && python run.py")
    print("2. Frontend: npm run dev")
    print("\nOr use Docker:")
    print("docker-compose up --build")

if __name__ == "__main__":
    main()

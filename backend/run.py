import uvicorn
import subprocess
import sys
import os
import signal
import time
from threading import Thread

def run_frontend():
    # Change to the root directory where package.json is located
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Start npm run dev
    subprocess.run(["npm", "run", "dev"], shell=True)

def run_backend():
    # Change back to the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    # Start frontend in a separate thread
    frontend_thread = Thread(target=run_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()

    # Start backend in main thread
    try:
        run_backend()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)

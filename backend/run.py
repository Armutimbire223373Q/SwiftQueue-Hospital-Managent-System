import uvicorn
import sys
import os
import signal

def run_backend():
    # Stay in the backend directory
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=False)

if __name__ == "__main__":
    # Start backend serving both API and frontend
    try:
        run_backend()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)

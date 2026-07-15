import subprocess
import time
import sys
import os
import signal

processes = []

def run_process(cmd, name):
    print(f"Starting {name}: {cmd}")
    try:
        p = subprocess.Popen(cmd, shell=True)
        processes.append(p)
        return p
    except Exception as e:
        print(f"Failed to start {name}: {e}")
        return None

def main():
    redis_path = "redis-server"
    winget_redis = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\taizod1024.redis-windows-fork_Microsoft.Winget.Source_8wekyb3d8bbwe\Redis-8.8.0-Windows-x64-msys2\redis-server.exe"
    )
    if os.path.exists(winget_redis):
        redis_path = f'"{winget_redis}"'
        print(f"Located local Redis server installation at: {winget_redis}")
    
    
    run_process(f"{redis_path}", "Redis Server")
    time.sleep(2) 

    
    python_exe = os.path.join("venv", "Scripts", "python.exe")
    celery_exe = os.path.join("venv", "Scripts", "celery.exe")
    
    if not os.path.exists(python_exe):
        print("Error: Virtual environment not found in './venv'. Please create and install requirements first.")
        sys.exit(1)

    
    run_process(f"{celery_exe} -A backend.tasks.celery_app worker --loglevel=info -P solo", "Celery Worker")
    
    run_process(f"{celery_exe} -A backend.tasks.celery_app beat --loglevel=info", "Celery Beat")

    run_process(f"{python_exe} -m backend.app", "Flask App (Aarohan Setu 2.0)")

    print("Aarohan Setu 2.0 Placement Portal is booting up!")
    print("UI & API: http://localhost:5001/")
    print("Press Ctrl+C in this terminal to shut down all services.")

    try:
        while True:
            for p in processes:
                if p.poll() is not None:
                    print(f"One of the background services has stopped. Shutting down all...")
                    raise KeyboardInterrupt
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all processes...")
        for p in processes:
            try:
                if sys.platform == "win32":
                    subprocess.run(f"taskkill /F /T /PID {p.pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    p.terminate()
            except Exception as e:
                print(f"Error terminating process: {e}")
        print("Goodbye!")

if __name__ == '__main__':
    main()

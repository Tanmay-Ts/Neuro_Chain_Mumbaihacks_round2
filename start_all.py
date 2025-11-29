import subprocess
import sys
import time
import os

def start_services():
    print("🚀 Starting NeuroChain System...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    scheduler = subprocess.Popen([sys.executable, os.path.join(base_dir, "scheduler_service.py")], cwd=base_dir)
    streamlit = subprocess.Popen([sys.executable, "-m", "streamlit", "run", os.path.join(base_dir, "app.py")], cwd=base_dir, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)

    print("✅ Services started.")
    try:
        while True:
            time.sleep(2)
            if scheduler.poll() is not None:
                print("⚠️ Scheduler crashed!")
                break
            if streamlit.poll() is not None:
                print("⚠️ Dashboard stopped!")
                break
    except KeyboardInterrupt:
        print("🛑 Stopping...")
        scheduler.terminate()
        streamlit.terminate()

if __name__ == "__main__":
    start_services()
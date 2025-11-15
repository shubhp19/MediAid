import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
        print("Starting Gradio app...")
        self.process = subprocess.Popen([sys.executable, self.script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # Give the app a moment to start
        # Print the output to find the Gradio URL
        for line in self.process.stdout:
            line = line.decode().strip()
            if "Running on local URL" in line or "Running on public URL" in line:
                print(line)
            if "Running on public URL" in line:
                self.url = line.split()[-1]
                print(f"Open this URL in your browser: {self.url}")

    def on_modified(self, event):
        if event.src_path.endswith("gradio_app.py"):
            print("Detected change in gradio_app.py, restarting...")
            self.start_process()

if __name__ == "__main__":
    script_to_run = "gradio_app.py"
    event_handler = RestartHandler(script_to_run)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    print("Monitoring for changes in gradio_app.py... Save the file to reload the app.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
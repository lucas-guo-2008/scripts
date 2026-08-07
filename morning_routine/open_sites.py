import webbrowser
import subprocess
import time

subprocess.run(["open", "-na", "Google Chrome", "--args", "--new-window", "about:blank"])
time.sleep(1)
webbrowser.open('https://youtube.com', 0)
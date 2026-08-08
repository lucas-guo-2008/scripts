import webbrowser
import subprocess
import time
from pynput import keyboard

sites = ["gmail.com", "outlook.office.com", "calendar.google.com"]

subprocess.run(["open", "-na", "Google Chrome", "--args", "--new-window", "about:blank"])

for site in sites:
  time.sleep(0.5)
  webbrowser.open("https://"+site)

def on_press(key):
  if key == keyboard.Key.esc:
    subprocess.run(["open", "-a", "Reminders"])
    return False

listener = keyboard.Listener(on_press=on_press)
listener.start()

try:
  while listener.is_alive():
    time.sleep(1)
except KeyboardInterrupt:
  listener.stop()
import webbrowser
import subprocess
import time

sites = ["gmail.com", "outlook.office.com", "calendar.google.com"]

subprocess.run(["open", "-na", "Google Chrome", "--args", "--new-window", "about:blank"])

for site in sites:
  time.sleep(0.5)
  webbrowser.open("https://"+site)

time.sleep(2)
subprocess.run(["open", "-a", "Reminders"])

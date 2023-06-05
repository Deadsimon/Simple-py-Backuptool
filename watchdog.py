import subprocess
import time
import os

watchdog_dir = os.path.dirname(os.path.abspath(__file__))
quickrun_path = os.path.join(watchdog_dir, "Quickrun", "quickrun.exe")
backup_path = os.path.join(watchdog_dir, "Backup", "backup.exe")

def is_process_running(process_name):
    try:
        output = subprocess.check_output('tasklist', shell=True)
        if process_name in str(output):
            return True
    except subprocess.CalledProcessError:
        pass
    return False

def start_backup():
    print("Starting Backup.exe...")
    subprocess.Popen([backup_path])

def start_quickrun():
    print("Starting QuickRun.exe...")
    subprocess.Popen([quickrun_path])
    time.sleep(10)  # Wait for QuickRun.exe to execute

def watchdog():
    start_quickrun()  # Run QuickRun.exe before starting the loop
    while True:
        if is_process_running('Backup.exe'):
            print("Backup.exe is running. Sleeping for 10 seconds...")
            time.sleep(10)
        else:
            start_backup()

watchdog()

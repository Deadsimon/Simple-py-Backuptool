import subprocess
import time

def is_process_running(process_name):
    try:
        # Run the tasklist command to check if the process is running
        output = subprocess.check_output('tasklist', shell=True)
        if process_name in str(output):
            return True
    except subprocess.CalledProcessError:
        pass
    return False

def start_backup():
    # Start Backup.exe
    print("Starting Backup.exe...")
    subprocess.Popen(['Backup.exe'])

def start_quickrun():
    # Start QuickRun.exe
    print("Starting QuickRun.exe...")
    subprocess.Popen(['QuickRun.exe'])
    print("Waiting for QuickRun.exe to finish...")
    while is_process_running('QuickRun.exe'):
        time.sleep(10)

def watchdog():
    while True:
        if is_process_running('Backup.exe'):
            print("Backup.exe is running. Sleeping for 10 seconds...")
            time.sleep(10)
        else:
            start_quickrun()
            start_backup()

watchdog()

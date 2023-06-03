import os
import shutil
import zipfile
import datetime
import schedule
import time
import keyboard
import yaml


def backup_folder(folder_path, output_folder):
    # Get the folder name
    folder_name = os.path.basename(folder_path)

    # Create a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create the zip file name
    zip_file_name = f"{folder_name}_{timestamp}.zip"

    # Create the output path
    output_path = os.path.join(output_folder, zip_file_name)

    # Create a temporary folder for storing files
    temp_folder = os.path.join(os.getcwd(), "__temp")
    os.makedirs(temp_folder, exist_ok=True)

    try:
        # Copy all files and subdirectories to the temporary folder
        shutil.copytree(folder_path, os.path.join(temp_folder, folder_name))

        # Create a zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files and subdirectories to the zip file
            for root, dirs, files in os.walk(temp_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, temp_folder))

        print(f"Backup created: {output_path}")

    finally:
        # Remove the temporary folder
        shutil.rmtree(temp_folder)


def backup_job(folder_path, output_folder):
    backup_folder(folder_path, output_folder)
    schedule_next_job(folder_path, output_folder)


def schedule_next_job(folder_path, output_folder, schedule_length):
    schedule.clear()
    schedule.every().interval(schedule_length).do(
        backup_job, folder_path=folder_path, output_folder=output_folder
    )


def read_config(file_path):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


# Read the configuration from the YAML file
config = read_config('config.yml')
output_folder = config['output_folder']
backup_folder = config['backup_folder']
schedule_length = config['schedule_length']

# Usage example
folder_path = os.path.expandvars(backup_folder)

# Schedule the initial backup job
schedule.every().interval(schedule_length).do(
    backup_job, folder_path=folder_path, output_folder=output_folder
)

print("Backup job is scheduled. Press ESC to stop the application.")

while True:
    next_run = schedule.next_run()
    next_run_formatted = next_run.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Next backup scheduled at: {next_run_formatted}")

    schedule.run_pending()
    time.sleep(1)
    if keyboard.is_pressed('esc'):
        print("Application stopped.")
        break

import os
import shutil
import zipfile
import datetime
import sqlite3
import schedule
import time
from threading import Thread

db_file_path = r"C:\Program Files\Deadsimon - Github\Simple-py-backer-upper\backup_status.db"

def initialize_database():
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS backups
                 (scheduled_time TEXT, status TEXT)''')

    conn.commit()
    conn.close()


def update_backup_status(scheduled_time, status):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Check if the scheduled_time exists in the database
    cursor.execute("SELECT COUNT(*) FROM backups WHERE scheduled_time = ?", (scheduled_time,))
    row_count = cursor.fetchone()[0]

    if row_count > 0:
        # Update the existing entry
        cursor.execute("UPDATE backups SET status = ? WHERE scheduled_time = ?", (status, scheduled_time))
        conn.commit()
        print(f"Updated status for backup scheduled at: {scheduled_time}")
    else:
        # Insert a new entry
        cursor.execute("INSERT INTO backups (scheduled_time, status) VALUES (?, ?)", (scheduled_time, status))
        conn.commit()
        print(f"Created new backup entry at: {scheduled_time}")

    if status.startswith('Failed'):
        # Delete any rows with a pending status
        cursor.execute("DELETE FROM backups WHERE status = ?", ('Pending',))
        conn.commit()
        print("Deleted pending backup entries")

    conn.close()


def check_outstanding_backups():
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()

    # Get the current time
    current_time = datetime.datetime.now()

    # Fetch all pending backups with scheduled time in the past
    c.execute('SELECT scheduled_time FROM backups WHERE status = ? AND scheduled_time < ?',
              ('Pending', current_time))

    pending_backups = c.fetchall()

    if pending_backups:
        print(f'{len(pending_backups)} outstanding backup(s) found.')

    for backup in pending_backups:
        scheduled_time_str = backup[0]  # Get the scheduled time as string
        scheduled_time_str = scheduled_time_str.split('.')[0]  # Remove microseconds from the string
        scheduled_time = datetime.datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S")  # Convert to datetime object
        print(f'Scheduled backup at {scheduled_time} is overdue. Marking as Failed.')
        update_backup_status(scheduled_time_str, f'Failed_{datetime.datetime.now()}')

    conn.close()




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
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    zipf.write(file_path, os.path.relpath(file_path, temp_folder))

        print(f"Backup created: {output_path}")
        return output_path

    except Exception as e:
        print(f"Backup failed: {e}")
        return False

    finally:
        # Remove the temporary folder
        shutil.rmtree(temp_folder)


def backup_job(folder_path, output_folder, scheduled_time_str):
    # Establish a connection and create a cursor
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()

    # Perform the backup process
    backup_filename = backup_folder(folder_path, output_folder)

    # Update the backup status to 'Success' or 'Failed' after the backup process is completed
    if backup_filename:
        update_backup_status(scheduled_time_str, f'Success_{datetime.datetime.now()}')
    else:
        update_backup_status(scheduled_time_str, f'Failed_{datetime.datetime.now()}')

    # Close the connection
    conn.close()

    # Schedule the next backup job
    schedule_next_job(folder_path, output_folder, schedule_length_unit, schedule_length_amount)


def schedule_next_job(folder_path, output_folder, sch_length_unit, sch_length_amount):
    # Calculate the next scheduled time
    current_time = datetime.datetime.now()

    if sch_length_unit.endswith("s"):
        plural_schedule_length_unit = sch_length_unit
    else:
        plural_schedule_length_unit = f"{sch_length_unit}s"

    delta_args = {plural_schedule_length_unit: sch_length_amount}
    schedule_length = datetime.timedelta(**delta_args)
    next_time = current_time + schedule_length

    # Update the backup status to Pending
    update_backup_status(next_time.strftime("%Y-%m-%d %H:%M:%S.%f"), 'Pending')

    # Schedule the backup job
    print(f"Next backup scheduled at: {next_time}")
    scheduler = schedule.Scheduler()

    scheduler.every().day.at(next_time.strftime("%H:%M")).do(
        backup_job, folder_path, output_folder, next_time.strftime("%Y-%m-%d %H:%M:%S.%f"))

    # Check for outstanding backups
    check_outstanding_backups()

    # Run the scheduler in a separate thread
    def run_scheduler():
        while True:
            scheduler.run_pending()
            time.sleep(1)

    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()


def cleanup():
    # Cleanup function to ensure pending changes are committed to the database
    conn = sqlite3.connect(db_file_path)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Read the configuration from config.yml
    config_file_path = r"C:\Program Files\Deadsimon - Github\Simple-py-backer-upper\config.yml"

    import yaml

    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)

    # Remove the following lines to resolve the shadowing issue
    # folder_path = config['folder_path']
    # output_folder = config['output_folder']

    schedule_length_unit = config['schedule_length_unit']
    schedule_length_amount = config['schedule_length_amount']

    # Initialize the database
    initialize_database()

    # Schedule the first backup job
    schedule_next_job(config['folder_path'], config['output_folder'], schedule_length_unit, schedule_length_amount)

    print("Backup job is scheduled. Press ESC to stop the application.")

    # Keep the application running until the user presses ESC
    try:
        while True:
            if input() == '\x1b':
                cleanup()  # Call the cleanup function before exiting
                break
    except KeyboardInterrupt:
        cleanup()  # Call the cleanup function before exiting

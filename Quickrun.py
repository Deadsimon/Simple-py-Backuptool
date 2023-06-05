import os
import shutil
import zipfile
import yaml
import random
import string
from datetime import datetime

def generate_random_string(length):
    """Generate a random string of specified length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def generate_unique_temp_directory(output_folder):
    """Generate a unique temporary directory name."""
    while True:
        temp_directory_name = f"_temp_{generate_random_string(6)}"
        temp_directory = os.path.join(output_folder, temp_directory_name)
        if not os.path.exists(temp_directory):
            return temp_directory

def backup_directory(folder_path, output_folder):
    # Create a timestamp in the desired format
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create a zip file with the name of the source directory and timestamp
    base_folder_name = os.path.basename(folder_path)
    zip_file_name = f"{base_folder_name}_{timestamp}_QR.zip"
    zip_file_path = os.path.join(output_folder, zip_file_name)

    # Create a unique temporary directory to store the files before zipping
    temp_directory = generate_unique_temp_directory(output_folder)
    os.makedirs(temp_directory)

    try:
        # Copy all the files and subdirectories to the temporary directory
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                src_file_path = os.path.join(root, file)
                dst_file_path = os.path.join(temp_directory, os.path.relpath(src_file_path, folder_path))
                os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
                shutil.copy2(src_file_path, dst_file_path)

        # Create a zip file and add all the files in the temporary directory to it
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_directory)
                    zipf.write(file_path, arcname)

        print(f"Backup created: {zip_file_path}")
    finally:
        # Remove the temporary directory
        shutil.rmtree(temp_directory)

if __name__ == "__main__":
    # Read the configuration from the YAML file
    with open("config.yml", "r") as config_file:
        config = yaml.safe_load(config_file)

    folder_path = os.path.expanduser(config["folder_path"])  # Use os.path.expanduser to handle Windows paths
    output_folder = os.path.expanduser(config["output_folder"])

    backup_directory(folder_path, output_folder)

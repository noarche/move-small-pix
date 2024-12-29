import os
import shutil
import time
from PIL import Image
from tqdm import tqdm
from datetime import datetime
from colorama import Fore, Style, init
import argparse

init(autoreset=True)

def get_image_formats():
    formats = list(Image.registered_extensions().keys())
    return [f.lower() for f in formats] + [".webp"]

def prompt_user(message, default=None, convert_type=str):
    while True:
        user_input = input(Fore.CYAN + message + Style.RESET_ALL).strip()
        if not user_input and default is not None:
            return default
        try:
            return convert_type(user_input)
        except ValueError:
            print(Fore.RED + "Invalid input. Please try again." + Style.RESET_ALL)

def get_file_size_kb(file_path):
    return os.path.getsize(file_path) / 1024

def delete_empty_dirs(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if not dirnames and not filenames:
            os.rmdir(dirpath)
            print(Fore.MAGENTA + f"Deleted empty directory: {dirpath}" + Style.RESET_ALL)

def show_help():
    help_text = """
    This script scans a directory for image files and moves or copies images smaller than a specified size to a new directory.

    Usage:
        - The script will prompt for a directory to scan.
        - It will identify all image files in the directory and subdirectories.
        - You can specify a minimum file size in KB (default is 90 KB).
        - The script will move or copy files smaller than the specified size to a new directory named with the current timestamp.

    Features:
        - Supports common image formats including .webp.
        - Displays statistics such as the total number of images found, moved, and their average sizes.
        - Offers an option to process another directory after completion.
        - Optionally deletes empty directories after processing.
        - Color-coded minimal text output for better readability.

    Arguments:
        -h, --help: Display this help message and exit.
    """
    print(Fore.GREEN + help_text + Style.RESET_ALL)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true", help="Show help information about the script.")
    args = parser.parse_args()

    if args.help:
        show_help()
        return

    while True:
        root_dir = prompt_user("Enter the directory to scan for images: ")
        if not os.path.isdir(root_dir):
            print(Fore.RED + "Invalid directory. Please try again." + Style.RESET_ALL)
            continue

        min_size_kb = prompt_user("Enter minimum file size in KB (default: 90KB): ", default=90, convert_type=int)
        move_files = prompt_user("Do you want to move the original files? (y/n, default: n): ", default="n", convert_type=str).lower() == "y"

        image_formats = get_image_formats()
        files_found = 0
        files_moved = 0
        files_found_data = []  # List to store (file_path, file_size_kb)
        files_moved_data = []  # List to store (file_path, file_size_kb)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_dir = os.path.join(root_dir, timestamp)
        os.makedirs(destination_dir, exist_ok=True)

        print(Fore.GREEN + "Scanning for images..." + Style.RESET_ALL)

        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if os.path.splitext(filename.lower())[1] in image_formats:
                    file_path = os.path.join(dirpath, filename)
                    file_size_kb = get_file_size_kb(file_path)
                    files_found += 1
                    files_found_data.append((file_path, file_size_kb))

                    if file_size_kb < min_size_kb:
                        new_file_name = f"{os.path.basename(root_dir)}_{filename}"
                        new_file_path = os.path.join(destination_dir, new_file_name)
                        shutil.move(file_path, new_file_path) if move_files else shutil.copy(file_path, new_file_path)
                        files_moved += 1
                        files_moved_data.append((file_path, file_size_kb))

        # Display summary
        print(Fore.YELLOW + f"Total images found: {files_found}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Total images moved: {files_moved}" + Style.RESET_ALL)

        for fmt in image_formats:
            count_found = sum(1 for f, _ in files_found_data if os.path.splitext(f.lower())[1] == fmt)
            count_moved = sum(1 for f, _ in files_moved_data if os.path.splitext(f.lower())[1] == fmt)
            if count_found > 0:
                print(Fore.BLUE + f"{fmt.upper()} - Found: {count_found}, Moved: {count_moved}" + Style.RESET_ALL)

        avg_size_found = sum(size for _, size in files_found_data) / len(files_found_data) if files_found_data else 0
        avg_size_moved = sum(size for _, size in files_moved_data) / len(files_moved_data) if files_moved_data else 0

        print(Fore.YELLOW + f"Average size of images found: {avg_size_found:.2f} KB" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Average size of images moved: {avg_size_moved:.2f} KB" + Style.RESET_ALL)

        # Prompt to delete empty directories
        delete_empty = prompt_user("Do you want to delete empty directories? (y/n, default: n): ", default="n", convert_type=str).lower() == "y"
        if delete_empty:
            delete_empty_dirs(root_dir)

        # Prompt for next action
        next_action = prompt_user("Do you want to process another directory? (e to exit, any key to continue): ", default="n", convert_type=str).lower()
        if next_action == "e":
            print(Fore.GREEN + "Exiting. Goodbye!" + Style.RESET_ALL)
            break

if __name__ == "__main__":
    main()

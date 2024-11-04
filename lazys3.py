#!/usr/bin/env python3
import os
import configparser
from tabulate import tabulate
from colorama import init, Fore, Style
import subprocess
import threading
import boto3
import time
import random

# Initialize Colorama
init(autoreset=True)

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[93m'
    RED = '\033[1;31m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    END = '\033[0m'

colors = [Color.RED, Color.YELLOW, Color.GREEN, Color.CYAN, Color.BLUE]
message = f"""
{Color.BLINK}           
░▒▓█▓▒░       ░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓███████▓▒░▒▓███████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓██▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓████████▓▒░  ░▒▓██▓▒░   ░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓███████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░░▒▓██▓▒░       ░▒▓█▓▒░          ░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░          ░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░  ░▒▓█▓▒░   ░▒▓███████▓▒░░▒▓███████▓▒░  
                                                                                
®2024🇲🇾"""

def display_banner():
    while True:
        for color in colors:
            print(color + message + Color.END, end='\r')
            time.sleep(1)
            print(' ' * 80, end='\r')
def load_aws_credentials():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.aws/credentials"))
    profiles = config.sections()
    return profiles

def login_to_s3(profile):
    session = boto3.Session(profile_name=profile)
    s3 = session.client('s3')
    return s3

def list_buckets(s3):
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets

def list_objects_in_bucket(s3, bucket_name, prefix=None):
    if prefix:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    else:
        response = s3.list_objects_v2(Bucket=bucket_name)
    objects = []
    if 'Contents' in response:
        objects = [(obj['Key'], obj['Size']) for obj in response['Contents']]
    return objects

def list_directories_in_bucket(s3, bucket_name, prefix=None):
    if prefix:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    else:
        response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
    directories = []
    if 'CommonPrefixes' in response:
        directories = [directory['Prefix'] for directory in response['CommonPrefixes']]
    return directories

def download_object(s3, bucket_name, object_key, local_directory):
    local_filename = os.path.join(local_directory, os.path.basename(object_key))
    s3.download_file(bucket_name, object_key, local_filename)
    return local_filename

def download_directory(s3, bucket_name, directory_prefix, local_directory):
    objects = list_objects_in_bucket(s3, bucket_name, directory_prefix)
    for obj_key, _ in objects:
        download_object(s3, bucket_name, obj_key, local_directory)

def download_all_objects(s3, bucket_name, local_directory):
    objects = list_objects_in_bucket(s3, bucket_name)
    for obj_key, _ in objects:
        download_object(s3, bucket_name, obj_key, local_directory)

def prompt_keep_or_delete(image_path):
    while True:
        choice = input("Do you want to keep the downloaded image? (y/n): ").strip().lower()
        if choice == 'y':
            print("Image kept.")
            break
        elif choice == 'n':
            os.remove(image_path)
            print("Image deleted.")
            break
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")

def navigate_directories(s3, bucket_name, base_directory=""):
    current_directory = base_directory
    while True:
        directories = list_directories_in_bucket(s3, bucket_name, current_directory)
        print("\nDirectories:")
        print(tabulate(enumerate(directories, start=1), headers=["#", "Directory"], tablefmt="fancy_grid"))
        print("Options:")
        print("1. List Files")
        print("2. Go to Subdirectory")
        print("3. Go Up to Parent Directory")
        print("4. Exit Navigation")
        choice = input("Enter your choice: ")
        if choice == '1':
            objects = list_objects_in_bucket(s3, bucket_name, current_directory)
            print(tabulate(enumerate(objects, start=1), headers=["#", "Object Key", "Size"], tablefmt="fancy_grid"))
        elif choice == '2':
            subdirectory_choice = int(input("Enter the number corresponding to the subdirectory you want to navigate to: "))
            current_directory = directories[subdirectory_choice - 1]
        elif choice == '3':
            if current_directory:
                current_directory = os.path.dirname(current_directory.rstrip('/')) + '/'
            else:
                print("You are already in the root directory.")
        elif choice == '4':
            print("Exiting navigation.")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    banner_thread = threading.Thread(target=display_banner)
    banner_thread.daemon = True
    banner_thread.start()

    profiles = load_aws_credentials()
    
    if not profiles:
        print("No profiles found in the AWS credentials file.")
        return

    print("Available AWS Profiles:")
    for i, profile in enumerate(profiles, start=1):
        print(f"{i}. {profile}")

    profile_choice = int(input("Enter the number corresponding to the profile you want to use: "))
    selected_profile = profiles[profile_choice - 1]
    
    s3 = login_to_s3(selected_profile)

    while True:
        print("\nOptions:")
        print("1. List Buckets")
        print("2. List Objects in a Bucket")
        print("3. Navigate Directories in a Bucket")
        print("4. Download Object")
        print("5. Download Directory")
        print("6. Download All Objects in a Bucket")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            buckets = list_buckets(s3)
            print(tabulate(enumerate(buckets, start=1), headers=["#", "Bucket Name"], tablefmt="fancy_grid"))
        elif choice == '2':
            bucket_name = input("Enter bucket name: ")
            objects = list_objects_in_bucket(s3, bucket_name)
            print(tabulate(enumerate(objects, start=1), headers=["#", "Object Key", "Size"], tablefmt="fancy_grid"))
        elif choice == '3':
            bucket_name = input("Enter bucket name: ")
            navigate_directories(s3, bucket_name)
        elif choice == '4':
            bucket_name = input("Enter bucket name: ")
            object_key = input("Enter the object key to download: ")
            local_directory = input("Enter the local directory to save the file: ")
            download_object(s3, bucket_name, object_key, local_directory)
        elif choice == '5':
            bucket_name = input("Enter bucket name: ")
            directory_prefix = input("Enter the directory prefix to download: ")
            local_directory = input("Enter the local directory to save the files: ")
            download_directory(s3, bucket_name, directory_prefix, local_directory)
        elif choice == '6':
            bucket_name = input("Enter bucket name: ")
            local_directory = input("Enter the local directory to save the files: ")
            download_all_objects(s3, bucket_name, local_directory)
        elif choice == '7':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

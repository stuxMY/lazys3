#!/usr/bin/env python3
import os
import configparser
from tabulate import tabulate
from colorama import init, Fore, Back, Style
import subprocess

import boto3
import time
import random

print("""
🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
🟥🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
🟥🟥🟥🟥⬜⬜⬜⬜⬜⬜⬜⬜⬜
🟥🟥🟥🟥🟥⬜⬜⬜⬜⬜⬜⬜⬜
🟥🟥🟥🟥⬜⬜⬜⬜⬜⬜⬜⬜⬜
🟥🟥🟥🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟥🟥🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟥🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 ® Free Palestine
      
░▒▓█▓▒░       ░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓███████▓▒░▒▓███████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓██▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓████████▓▒░  ░▒▓██▓▒░   ░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓███████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░░▒▓██▓▒░       ░▒▓█▓▒░          ░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░          ░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░  ░▒▓█▓▒░   ░▒▓███████▓▒░░▒▓███████▓▒░  
                                                                                
    """)

def load_aws_credentials():
    """
    Load AWS credentials from the default AWS credentials file (~/.aws/credentials).
    """
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.aws/credentials"))
    profiles = config.sections()
    return profiles

def login_to_s3(profile):
    """
    Log in to AWS S3 using credentials from the specified profile.
    """
    session = boto3.Session(profile_name=profile)
    s3 = session.client('s3')
    return s3

def list_buckets(s3):
    """
    List all buckets in the S3 account.
    """
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets

def list_objects_in_bucket(s3, bucket_name, prefix=None):
    """
    List objects in a specified S3 bucket.
    """
    if prefix:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    else:
        response = s3.list_objects_v2(Bucket=bucket_name)
    objects = []
    if 'Contents' in response:
        objects = [(obj['Key'], obj['Size']) for obj in response['Contents']]
    return objects

def list_directories_in_bucket(s3, bucket_name, prefix=None):
    """
    List directories in a specified S3 bucket.
    """
    if prefix:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    else:
        response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
    directories = []
    if 'CommonPrefixes' in response:
        directories = [directory['Prefix'] for directory in response['CommonPrefixes']]
    return directories

def download_object(s3, bucket_name, object_key, local_directory):
    """
    Download an object from a specified S3 bucket.
    """
    local_filename = os.path.join(local_directory, os.path.basename(object_key))
    s3.download_file(bucket_name, object_key, local_filename)
    return local_filename

def download_directory(s3, bucket_name, directory_prefix, local_directory):
    """
    Download all objects within a directory from a specified S3 bucket.
    """
    objects = list_objects_in_bucket(s3, bucket_name, directory_prefix)
    for obj_key, _ in objects:
        download_object(s3, bucket_name, obj_key, local_directory)

def download_all_objects(s3, bucket_name, local_directory):
    """
    Download all objects within a bucket to the specified local directory.
    """
    objects = list_objects_in_bucket(s3, bucket_name)
    for obj_key, _ in objects:
        download_object(s3, bucket_name, obj_key, local_directory)

def change_color():
    """
    Change the color of the table lines.
    """
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    return random.choice(colors)

def prompt_keep_or_delete(image_path):
    """
    Prompt the user to keep or delete the downloaded image.
    """
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
    """
    Navigate directories within a bucket.
    """
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

    color_timer = 5  # Change color every 5 seconds
    start_time = time.time()

    while True:
        print("\nOptions:")
        print("1. List Buckets")
        print("2. List Objects in a Bucket")
        print("3. Navigate Directories in a Bucket")
        print("4. Download Object")
        print("5. Download Directory")
        print("6. Download All Objects in a Bucket")  # Added option
        print("7. Exit")

        elapsed_time = time.time() - start_time
        if elapsed_time > color_timer:
            start_time = time.time()
            color = change_color()
        else:
            color = Fore.RESET

        choice = input(f"{color}Enter your choice: ")

        if choice == '1':
            buckets = list_buckets(s3)
            print(tabulate(enumerate(buckets, start=1), headers=["#", "Bucket Name"], tablefmt="fancy_grid"))
        elif choice == '2':
            bucket_name = input("Enter bucket name: ")
            objects = list_objects_in_bucket(s3, bucket_name)
            print(tabulate(enumerate(objects, start=1), headers=["#", "Object Key", "Size"], tablefmt="fancy_grid"))
        elif choice == '3':
            bucket_name = input("Enter bucket name: ")
            base_directory = input("Enter base directory (optional): ")
            navigate_directories(s3, bucket_name, base_directory)
        elif choice == '4':
            bucket_name = input("Enter bucket name: ")
            object_key = input("Enter object key: ")
            local_directory = input("Enter local directory to save: ")
            local_filename = download_object(s3, bucket_name, object_key, local_directory)
            print(f"Object '{object_key}' downloaded as '{local_filename}'")
        elif choice == '5':
            bucket_name = input("Enter bucket name: ")
            directory_prefix = input("Enter directory prefix: ")
            local_directory = input("Enter local directory to save: ")
            download_directory(s3, bucket_name, directory_prefix, local_directory)
            print(f"Directory '{directory_prefix}' downloaded to '{local_directory}'")
        elif choice == '6':
            bucket_name = input("Enter bucket name: ")
            local_directory = input("Enter local directory to save: ")
            download_all_objects(s3, bucket_name, local_directory)
            print(f"All objects in bucket '{bucket_name}' downloaded to '{local_directory}'")
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


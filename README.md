<div align="center">
    <a href="https://github.com/stuxMY/lazys3">
        <img src="https://i.ibb.co/FwLTX7G/Gemini-Generated-Image-iosg3qiosg3qiosg.jpg" alt="Logo" width="300" height="330">
    </a>
    <h3>LAZY S3</h3>
</div>

![Python Version](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Script Version](https://img.shields.io/badge/Version-v1.2.0-orange)


# LAZY S3 

A Python script to interact with AWS S3 buckets, allowing users to list buckets, navigate directories, and download objects and directories.

## Features

- List all S3 buckets in your AWS account.
- Navigate through directories within a specified S3 bucket.
- List objects in a bucket or a specific directory.
- Download individual objects or entire directories from S3.
- Download all objects within a bucket to a local directory.

## Prerequisites

- Python 3.x
- AWS account with S3 access.
- AWS CLI configured with profiles in `~/.aws/credentials`.

## Installation

1. Clone this repository:

   ```python3
   git clone https://github.com/stuxMY/lazys3.git
   cd lazys3
   pip install -r requirements.txt
   chmod +x lazys3.py
   ./lazys3.py
   


## Usage

Ensure your AWS credentials are set up correctly in ~/.aws/credentials. The format should be:
   ```python3
[profile_name]
aws_access_key_id=YOUR_ACCESS_KEY
aws_secret_access_key=YOUR_SECRET_KEY

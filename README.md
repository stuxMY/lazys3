<a href="https://github.com/astrdev/gitpy">
    <img src="https://i.ibb.co/wwjMFnD/Gemini-Generated-Image-fm13nrfm13nrfm13.jpg" alt="Logo" width="300" height="330">
</a>
<h3 align="center">LAZYS3</h3>

# LAZYS3 

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
   pip install boto3 tabulate colorama
   chmod +x lazys3.py
   ./lazys3.py



## Usage

Ensure your AWS credentials are set up correctly in ~/.aws/credentials. The format should be:
   ```python3
[profile_name]
aws_access_key_id=YOUR_ACCESS_KEY
aws_secret_access_key=YOUR_SECRET_KEY

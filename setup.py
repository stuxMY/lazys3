from setuptools import setup, find_packages

setup(
    name='lazys3',
    version='1.2.1',
    description='LAZYS3 is a powerful command-line tool designed for seamless interaction with Amazon S3 (Simple Storage Service)',
    author='stuxMY',
    packages=find_packages(),
    install_requires=[
        boto3
        colorama
        tabulate
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update as necessary
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',  # Update this to match your requirements
)

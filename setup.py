from setuptools import setup, find_packages
import os

# Get the directory of this file
current_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_dir, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(os.path.join(current_dir, "convolingo", "requirements.txt"), "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="convolingo",
    version="0.1.0",
    author="Convolingo Team",
    author_email="...", # No email for now
    description="Language Learning Assistant using VAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="...", # No URL for now
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "convolingo=convolingo.__main__:main",
        ],
    },
) 
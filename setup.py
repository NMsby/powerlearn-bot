"""
Setup script for PowerLearn LMS Bot.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="powerlearn-bot",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated login script for PowerLearn Project Academy LMS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/powerlearn-bot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: CC NY-NC-ND 4.0",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.50.0",
        "python-dotenv>=1.0.1",
        "PyYAML>=6.0.2",
        "pillow>=11.1.0",
    ],
    entry_points={
        "console_scripts": [
            "powerlearn-bot=src.main:main",
        ],
    },
)
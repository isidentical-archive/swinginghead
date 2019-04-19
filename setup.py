from pathlib import Path
from setuptools import setup, find_packages 

current_dir = Path(__file__).parent.resolve()

with open(current_dir / "README.md", encoding="utf-8") as f:
    long_description = f.read()
    
setup(
    name="shl",
    version="0.2",
    packages=find_packages(),
    url="https://github.com/btaskaya/swinginghead",
    description = "Swinging Head Language",
    long_description = long_description,
    long_description_content_type = "text/markdown",
)

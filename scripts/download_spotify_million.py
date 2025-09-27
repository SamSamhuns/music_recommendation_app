import kagglehub
import shutil
from pathlib import Path

# Download into KaggleHub cache
path = kagglehub.dataset_download("himanshuwagh/spotify-million")

# Define your custom destination
dest = Path("./data/spotify-million")
dest.mkdir(parents=True, exist_ok=True)

# Copy files from KaggleHub cache to your local folder
shutil.copytree(path, dest, dirs_exist_ok=True)

print("Dataset copied to:", dest)

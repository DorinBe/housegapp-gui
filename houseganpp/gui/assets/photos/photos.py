# Example assets.py
import os

photos_dir = os.path.dirname(__file__)
print(photos_dir)
house_icon = os.path.join(photos_dir, 'house_icon.ico')
house_logo = os.path.join(photos_dir, 'house_logo.png')
bg1 = os.path.join(photos_dir, 'bg1.png')
bg2 = os.path.join(photos_dir, 'bg2.png')
info = os.path.join(photos_dir, 'info.png')
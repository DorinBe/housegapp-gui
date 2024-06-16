# HouseGAN++ GUI Utility
Welcome to the **HouseGAN++ GUI Utility** repository! This project provides a graphical user interface (GUI) for the [HouseGAN++](https://github.com/ennauata/houseganpp) model, making it easier to generate and manipulate the input data for the model, allowing for easier post training. Our goal is to bridge the gap between cutting-edge AI research and practical applications in architecture and design. This project is contribution as part of our BSc in Software Engineering.

![Watch the video](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGtmaGkxaDR5NG55NzU5a3E5ZGZqMXFpamE5NXY5eWR2Z250dmhoeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qsbNaUqq56d5laejPT/giphy.gif)

## How to Use
- Load an existing JSON file, or start from scratch.
- Edit neighbors as necessary.
- Press the "generate locally" button, make sure you installed all the requirements in gui/houseganapp_min/requirements.txt file - i've changed it to run on CPU only for convenience. For more information check the [houseganpp](https://github.com/ennauata/houseganpp) state-of-the-art repository.
- GCP also availble, create a .env file with URL={cloud_run_url} and enter your cloud_run_url, if you have. Try using [House-GAN-Model](https://github.com/DorinBe/House-GAN-Model) on your google cloud account.

## Installing
- Developed with Python 3.10.11 on Windows 11.
- Install [GhostScript](https://www.ghostscript.com/)
- `pip install -r requirements.txt`
- Using [houseganpp](https://github.com/ennauata/houseganpp) model locally? Then also `pip install -r gui/houseganapp_min/requirements.txt`
- run gui/main.py

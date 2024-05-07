# houseganpp-gui-utility
Capstone Project Phase B. While experimenting with [houseganpp](https://github.com/ennauata/houseganpp) model, we struggled with editing the input data (JSONs). Hence, we developed a GUI utility for editing the JSONs according to the structure of the repository [houseganpp](https://github.com/ennauata/houseganpp).

![Watch the video](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGtmaGkxaDR5NG55NzU5a3E5ZGZqMXFpamE5NXY5eWR2Z250dmhoeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qsbNaUqq56d5laejPT/giphy.gif)

### Features
- User-friendly interface for navigating and modifying JSON files, which are the input data for [houseganpp](https://github.com/ennauata/houseganpp) model.
- Easy to compare between desired floorplan to output floorplan and graph.

### How to Use
- Launch the utility.
- Load an existing JSON file, or start from scratch.
- Edit the neighbours as necessary.
- Press the "generate locally" button, make sure you installed all the requirements in gui/houseganapp_min/requirements.txt file - i've changed it to run on CPU only for convenience. For more information check the [houseganpp](https://github.com/ennauata/houseganpp) state-of-the-art repository.
- GCP also availble, create a .env file with URL={cloud_run_url} and enter your cloud_run_url, if you have. Try using [House-GAN-Model](https://github.com/DorinBe/House-GAN-Model) on your google cloud account.

### Installing
- Developed with Python 3.10.11 on Windows 11.
- Install [GhostScript](https://www.ghostscript.com/)
- `pip install -r requirements.txt`
- Using [houseganpp](https://github.com/ennauata/houseganpp) model locally? Then also `pip install -r gui/houseganapp_min/requirements.txt`
- run gui/main.py

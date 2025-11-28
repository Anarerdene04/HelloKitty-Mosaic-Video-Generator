# HelloKitty-Mosaic-Video-Generator
The HelloKitty Mosaic Video Generator is a Python-based multimedia project that transforms a collection of Hello Kitty images and silhouette masks into an animated mosaic video (MP4).

Using Pillow, OpenCV, and NumPy, the script:

Builds mosaic images using small tile versions of plain Hello Kitty images

Applies a cinematic zoom-in → zoom-out animation to the first mosaic

Combines intro frames and mosaic frames into a complete video

This project explores image processing, animation logic, and Python-based video generation.

---

✨ Features

Mask-based mosaic rendering

Zoom-in / zoom-out animated intro

Intro section using plain high-resolution images

Multiple tile texture support

Automatic MP4 export with OpenCV

Fully configurable parameters

---

🗂 Folder Structure
project_root/
├─ hellokitty/
│  ├─ 001.jpg
│  ├─ kitty2.png
│  ├─ ...
│  ├─ mask1.png
│  ├─ mask2.png
│  └─ ...
├─ hellokitty_mosaic.py
└─ README.md

Rules

Plain images → filenames without "mask"

Mask images → filenames containing "mask"

---

⚙️ Configuration
PLAIN_COUNT    = 5
PLAIN_DURATION = 1500

TILE_W = 26
TILE_H = 26
GRID_STEP = 20

FPS = 10
BASE_TILE_COUNT = 5

ZOOM_IN_FACTOR = 5.0
ZOOM_OUT_STEPS = 10

Parameter	Description
PLAIN_COUNT	Number of intro frames
PLAIN_DURATION	Duration of intro images (ms)
TILE_W/H	Tile size
GRID_STEP	Mosaic density
FPS	Video FPS
BASE_TILE_COUNT	Number of tile images
ZOOM_IN_FACTOR	Initial zoom-in strength
ZOOM_OUT_STEPS	Smoothness of zoom-out
🧰 Used Technologies

Python 3.x

Pillow

OpenCV

NumPy

---

📥 Installation
pip install pillow opencv-python numpy


Then:

python hellokitty_mosaic.py


Produces:

hellokitty_mosaic.mp4

📸 Visual Example — How to Use

Below are the steps demonstrating how the HelloKitty Mosaic Generator works —
from preparing your images to producing the final MP4 output.

1. Prepare your images

Inside the hellokitty/ folder, include:

Several plain Hello Kitty images

One or more mask images (filenames must include "mask")

2. Adjust configuration (optional)

At the top of the script, you may adjust:

Tile size

Grid density

FPS

Zoom animation strength

Intro duration

3. Run the script
python hellokitty_mosaic.py


You will see console output indicating frame creation and processing.

4. Generate the mosaic from the mask

The script:

Reads the mask

Detects valid tile positions inside the silhouette

Places small tile images at each valid position to create a full mosaic

5. Zoom-in → Zoom-out animation

For the first mask:

A highly zoomed-in frame is created

The zoom is reduced step-by-step

Ending with a full mosaic frame for a smooth animated transition

6. Final MP4 output

After all frames are generated, the script exports:

hellokitty_mosaic.mp4


This file contains the intro section, mosaic sequences, and zoom animation.

🎥 Video Demonstration

▶ Full Demo Video:
https://www.instagram.com/XXXXXXXX


Replace the URL after uploading your final demonstration video.

---

🔍 How It Works — Short Overview

Detect plain vs mask images

Resize plain images into tiles

Process masks using thresholding + grid sampling

Place tiles according to valid silhouette coordinates

Generate zoom animation frames

Export all frames into an MP4 using OpenCV

---

📄 License

MIT License

---

🙏 Acknowledgements & References

https://pillow.readthedocs.io/

(Documentation for the Pillow library used for loading, resizing, and generating mosaic images.)

https://docs.opencv.org/

(OpenCV reference materials for video writing and MP4 generation.)

https://numpy.org/

(Useful documentation for array operations and PIL → OpenCV conversions.)

https://www.instagram.com/XXXXXXXX

(The Instagram Reel that inspired the visual idea of a Hello Kitty–shaped mosaic animation.)

https://readme.so

(Tool used to help structure and format this README.md file.)

Additional implementation and documentation help provided by ChatGPT.

# Thyra Web
a web version of [this program](https://github.com/marukoy-bot/Thyroid-Tumor-Binary-Classification-using-Machine-Learning), mainly for cross-platform compatibility

# Prerequisites
- Python 3.11.9 (somehow it doesn't work on versions 3.12+)

# Setting up
1. Create a folder to store the files, name it somethig like `thyra-web`
2. In this repo, click the `<> Code` button above and Download the `.zip` file
3. Extract the files of the `.zip` file inside the `thyra-web` folder. The file tree view should look something like this
<pre>
thyra-web
│   main.py
│   README.md
│   requirements.txt
│   start_server.py
│   thyroid_cancer_model.h5
│
├───static
│   │   logo.png
│   │   logo.svg
│   │   script.js
│   │   style.css
│   │
│   └───icons
│           dark_mode.svg
│           light_mode.svg
│
├───templates
│       index.html
│
└───__pycache__
        main.cpython-311.pyc
</pre>
# Running the program
1. Open a terminal in the `thyra-web` folder you created
2. Run the `start_server.py` script
   - Windows: `python start_server.py`
   - macOS: `python3.11 start_server.py`
4. Wait a bit. After it finishes setting up, your browser should automatically open with the THYRA website

# Operation
1. Get the thyroid ultrasound image.
2. You can:
   - Drag the image in the box
   - Click `📁 Browse` and search for the image
3. Click `🔍 Predict` button
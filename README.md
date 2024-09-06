Timer Application

A simple timer application that can be controlled via key bindings.
Displayed on top of other screens and can be modified via application settings.
Settings are accessible via system tray and right clicking the stopwatch icon. 

How to Run

To run the application, follow these steps:

1. **Download the code** from the repository.
2. **Run the application** by executing the following command:
   
   Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```
   Initialize main file
   ```bash
   python main.py
   ```
3. (Optional) install the executeable using nuitka and run Timer.exe from project folder.
   ```bash
   pip install nuitka
   ```
   ```bash
   python build_script.py
   ```
   To be able and use the application externally, wrap in a folder both icon files, config.txt and the executable.
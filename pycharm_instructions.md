# 🚀 PyCharm (Windows) Setup Guide

If you are using **PyCharm on Windows**, the setup process is much easier because PyCharm handles the virtual environment and command configurations automatically. Follow these steps:

### 1. Open the project in PyCharm
* Open PyCharm, click **Open**, and select your cloned project folder.

### 2. Configure the Virtual Environment (Python Interpreter)
PyCharm usually prompts you to create a virtual environment automatically when opening a new project. If it doesn't, follow these steps manually:
1. Go to **File** > **Settings** (or press `Ctrl + Alt + S`).
2. Navigate to **Project: your-repository-name** > **Python Interpreter**.
3. Click **Add Interpreter** (or the gear icon) > **Add Local Interpreter...**
4. Choose **Virtualenv Environment**, ensure **New environment** is selected, and click **OK**.
*(PyCharm will automatically create the `venv` folder and activate it for you).*

### 3. Install the dependencies
Once the interpreter is set up, you can install the packages:
1. Open the **Terminal** tab at the bottom of the PyCharm window (it will already have your `venv` activated).
2. Run the following command to install the required packages:
   ```cmd
   pip install -r requirements.txt
   ```

### 4. Run the application
In the terminal, type:
```bash
python app.py
```

Click the link in the PyCharm tool window to open **`http://127.0.0`** in your browser.

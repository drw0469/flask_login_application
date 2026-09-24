# 🚀 Windows Setup Guide

Follow these steps in your **Command Prompt** (cmd) to set up and run the Flask application locally on Windows.

### 1. Navigate into the project folder
Move into the root directory of the cloned repository:
```cmd
cd your-repository-name
```

### 2. Create a virtual environment
Isolate the project dependencies by creating a virtual environment:
```cmd
python -m venv .venv
```

### 3. Activate the virtual environment
Activate the environment so your packages install locally:
```cmd
.venv\Scripts\activate  
```
*(You will know it worked when `(.venv)` appears at the front of your terminal line.)*

### 4. Install the dependencies
Upgrade pip and install all required packages listed in the requirements file:
```cmd
python -m pip install --upgrade pip  # (optional)
pip install -r requirements.txt
```

### 6. Run the Flask application
Launch the local development server using the **app.py** entry file:
```cmd
flask run
```
or
```cmd
python app.py
```

Your app is now live! Open your browser and navigate to **`http://127.0.0`**.

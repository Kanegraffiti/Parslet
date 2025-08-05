# Parslet Installation Guide

This guide provides instructions for installing Parslet. The recommended method for most users is to install the package directly from PyPI using `pip`. For developers who wish to contribute or use the very latest version, instructions for installing from source are also provided.

---

## Recommended Installation (from PyPI)

This is the simplest and fastest way to get Parslet.

### On Linux, Windows, or macOS

Open your terminal and run:
```bash
pip install parslet
```

### On Android (via Termux)

Open Termux and run:
```bash
pip install parslet
```
> **Note:** Some features, like generating PNG images of workflows (`--export-png`), may require you to install Graphviz separately. In Termux, you can do this with `pkg install graphviz`.

After installation, you can verify it by running:
```bash
parslet --help
```

---

## Installation for Developers (from Source)

If you want to modify the code or contribute to Parslet, you should install it from the source code.

The general process for all platforms is:
1. Install prerequisite system tools (like Git and Python).
2. Clone the Parslet repository from GitHub.
3. Set up a Python virtual environment (highly recommended).
4. Install the required Python packages for development.
5. Install Parslet itself in "editable" mode.

---

### Android (via Termux)

Termux is a powerful terminal emulator for Android that provides a Linux-like environment, making it a perfect home for Parslet development.

**Step 1: Install and Update Termux**

If you haven't already, install Termux from F-Droid for the most up-to-date version. After installing, open Termux and update the package lists:

```bash
pkg update -y && pkg upgrade -y
```

**Step 2: Install Core Tools**

Install Python, Git, and essential build tools. These are needed to clone the repository and build some of Parslet's Python dependencies.

```bash
pkg install python git clang libjpeg-turbo libpng graphviz -y
```

**Step 3: Set Up Storage Access**

To allow Termux to access files on your phone's storage (e.g., in your `Downloads` or `Documents` folder), run:

```bash
termux-setup-storage
```

**Step 4: Clone the Parslet Repository**

Navigate to a directory where you want to store the project and clone it from GitHub.

```bash
# Example: cloning into your shared Documents folder
cd storage/shared/Documents
git clone https://github.com/Kanegraffiti/Parslet.git
cd Parslet
```

**Step 5: Set Up Virtual Environment and Install**

Create a virtual environment, activate it, and install the dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it (you must do this in every new session)
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Parslet in editable mode
pip install -e .
```

**Step 6: Verify Installation**

Check that the `parslet` command is available:

```bash
parslet --help
```

You are now ready to develop Parslet on Android!

---

### Linux (Debian/Ubuntu)

**Step 1: Install Core Tools**

Open your terminal and install Python, Git, and the necessary build tools using `apt`.

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git build-essential libjpeg-dev zlib1g-dev graphviz
```

**Step 2: Clone the Parslet Repository**

```bash
git clone https://github.com/Kanegraffiti/Parslet.git
cd Parslet
```

**Step 3: Set Up Virtual Environment and Install**

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Parslet in editable mode
pip install -e .
```

**Step 4: Verify Installation**

```bash
parslet --help
```

---

### Linux (Fedora/CentOS/RHEL)

**Step 1: Install Core Tools**

Open your terminal and install Python, Git, and build tools using `dnf` or `yum`.

```bash
# For Fedora
sudo dnf install -y python3 python3-pip git gcc-c++ libjpeg-turbo-devel zlib-devel graphviz

# For CentOS/RHEL
sudo yum install -y python3 python3-pip git gcc-c++ libjpeg-turbo-devel zlib-devel graphviz
```

**Step 2: Clone the Parslet Repository**

```bash
git clone https://github.com/Kanegraffiti/Parslet.git
cd Parslet
```

**Step 3: Set Up Virtual Environment and Install**

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Parslet in editable mode
pip install -e .
```

**Step 4: Verify Installation**

```bash
parslet --help
```

---

### Windows

For Windows, we recommend using **Git Bash**, which is included with Git for Windows, as it provides a Unix-like shell environment.

**Step 1: Install Git for Windows**

Download and install [Git for Windows](https://git-scm.com/download/win). This will also provide you with the **Git Bash** terminal.

**Step 2: Install Python**

Download and install the latest Python version from the [official Python website](https://www.python.org/downloads/windows/). **Important:** During installation, make sure to check the box that says "Add Python to PATH".

**Step 3: Install Graphviz (for PNG export)**

The `--export-png` feature requires Graphviz.
1. Download and run the installer from the [Graphviz download page](https://graphviz.org/download/).
2. Add the Graphviz `bin` directory to your system's PATH environment variable. The default path is usually `C:\Program Files\Graphviz\bin`.

**Step 4: Clone and Install Parslet**

Open **Git Bash** and follow these steps.

```bash
# Clone the repository
git clone https://github.com/Kanegraffiti/Parslet.git
cd Parslet

# Create and activate the virtual environment
python -m venv .venv
source .venv/Scripts/activate

# Install dependencies and Parslet
pip install -r requirements.txt
pip install -e .
```

**Step 5: Verify Installation**

```bash
parslet --help
```
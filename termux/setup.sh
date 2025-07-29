#!/data/data/com.termux/files/usr/bin/bash

# Parslet Environment Setup Script for Termux
# -------------------------------------------
# This script automates the setup of the necessary environment
# and dependencies for running Parslet and its examples on Termux.
#
# IMPORTANT PRE-REQUISITES:
# 1. Termux Installation: Ensure you have Termux installed (preferably from F-Droid for up-to-date versions).
# 2. Project Directory: This script ASSUMES it is being run from the ROOT DIRECTORY
#    of your cloned Parslet project. This is crucial for:
#    a. Correctly creating the virtual environment (e.g., in './.venv-parslet').
#    b. Finding 'requirements.txt' for installing Python dependencies.
#    c. Installing Parslet itself (e.g., 'pip install -e .').
# 3. Executable Permissions: Make this script executable before running. If you are in
#    the project root, you might run: chmod +x parslet/termux/setup.sh
#    Then execute it from the project root: ./parslet/termux/setup.sh

echo "🚀 Starting Parslet environment setup for Termux..."
echo "==================================================="

# Exit immediately if a command exits with a non-zero status.
# This ensures the script stops if any step fails, preventing further issues.
set -e

echo ""
echo "➡️ [1/5] Updating Termux packages..."
echo "------------------------------------"
# It's crucial to update and upgrade Termux's package lists and installed packages
# to ensure compatibility and security.
pkg update -y  # Fetches the newest versions of packages from repositories.
pkg upgrade -y # Upgrades all currently installed packages to their newest versions.
echo "✅ Termux packages updated."

echo ""
echo "➡️ [2/5] Installing core system tools (Python, git)..."
echo "-------------------------------------------------------"
# 'python' package in Termux provides the Python interpreter.
# 'git' is needed for version control, e.g., if you cloned the Parslet project repository.
# The '-y' flag automatically confirms any prompts.
pkg install python git -y
echo "✅ Core system tools (Python, Git) installed."

PY_VER=$(python -V 2>&1)
echo "Using $PY_VER"

# Verify pip installation. While usually bundled with 'python' in Termux, this is a safeguard.
# 'pip' is Python's package installer, essential for managing project dependencies from requirements.txt.
if ! command -v pip &> /dev/null; then
    echo "⚠️ pip command could not be found. Attempting to install 'python-pip' package..."
    pkg install python-pip -y # Explicitly install pip if it wasn't included with the main python package.
    if ! command -v pip &> /dev/null; then
        echo "❌ CRITICAL: pip installation failed even after attempting to install 'python-pip'."
        echo "   Please try to install pip manually or check your Termux Python installation, then re-run."
        exit 1 # Exit because pip is critical for next steps.
    fi
    echo "✅ pip (via 'python-pip' package) installed successfully."
fi


echo ""
echo "➡️ [3/5] Installing build dependencies for Python packages..."
echo "------------------------------------------------------------"
echo "This step installs system libraries needed for compiling some Python packages from source"
echo "(e.g., those with C extensions like Pillow, psutil, or parts of the scientific stack)."
# - build-essential & clang: Provide C/C++ compilers (gcc, g++) and related tools (make).
#   Essential for building many Python packages that include C/C++ extensions.
# - libjpeg-turbo & libpng: Image format libraries. Required by Pillow (Python Imaging Library),
#   which is used in Parslet's image processing examples.
# - zlib: A common compression library, also a frequent dependency for various packages.
# - libgfortran: Fortran library. Often needed for scientific Python packages like NumPy or SciPy
#   if they are built from source (though Parslet itself doesn't directly require them, they are common).
# - freetype: Font rendering library. Often a dependency for plotting libraries like Matplotlib.
# - graphviz: Toolkit for graph visualization. Required by Parslet's '--export-png' feature,
#   which uses the 'pydot' Python library. 'pydot' in turn calls Graphviz's 'dot' executable
#   to render PNG images from DOT language descriptions.
pkg install build-essential clang libjpeg-turbo libpng zlib freetype graphviz -y

# libgfortran has slightly different package names across Termux versions.
# Try a few common possibilities but continue even if none are found.
pkg install libgfortran -y || \
pkg install libgfortran5 -y || \
pkg install gfortran -y || \
echo "⚠️ libgfortran package not found. Continuing without it."

echo "✅ Build dependencies (compilers, image libs, Graphviz, etc.) installed."

echo ""
echo "➡️ [4/5] Setting up Python virtual environment (highly recommended)..."
echo "-------------------------------------------------------------------"
# Define a specific name for the virtual environment directory to avoid conflicts.
# This directory will be created in the current working directory (assumed to be project root).
VENV_DIR=".venv-parslet" 

if [ -d "$VENV_DIR" ]; then
    echo "ℹ️ Python virtual environment '$VENV_DIR' already exists in the current directory ($(pwd))."
    echo "   Skipping creation. If you wish to recreate it, please remove the directory first:"
    echo "   rm -rf $VENV_DIR"
else
    echo "Creating Python virtual environment in './$VENV_DIR'..."
    # 'python -m venv' is the standard and recommended way to create a virtual environment.
    # It ensures that pip, setuptools, and other necessary tools are correctly installed
    # within this isolated environment, specific to the Python version used to create it.
    python -m venv "$VENV_DIR"
    echo "✅ Virtual environment '$VENV_DIR' created successfully."
fi
echo ""
echo "📌 IMPORTANT: To activate the virtual environment, run the following command in your terminal:"
echo "   source $VENV_DIR/bin/activate"
echo ""
echo "   You must activate the virtual environment in each new Termux session before working"
echo "   with Parslet or installing its Python dependencies. Activation ensures that 'pip'"
echo "   installs packages into this isolated '$VENV_DIR' and that Python runs from it,"
echo "   preventing conflicts with system-wide packages or other projects."

echo ""
echo "➡️ [5/5] Next Steps & Important Notes:"
echo "---------------------------------------------------------------------"
echo "1. ❗️ CRITICAL FIRST STEP: Activate the virtual environment:"
echo "   source $VENV_DIR/bin/activate"
echo "   (If you skip this, dependencies and Parslet will likely be installed globally or not found correctly!)"
echo ""
echo "2. Install Python dependencies (once the venv is active):"
echo "   pip install -r requirements.txt"
echo "   (This file should be in your Parslet project root. It includes libraries like Pillow, psutil, pydot)."
echo ""
echo "3. Install Parslet itself (from the project root, with venv active):"
echo "   pip install -e .  # For an editable/developer install (recommended for contribution/local testing)"
echo "   # OR, for a standard user install into the venv (less common if you're running from the cloned repo):"
echo "   # pip install .     "
echo ""
echo "4. Verify installation and run examples (with venv active):"
echo "   parslet --help"
echo "   parslet run examples/hello.py --verbose"
echo "   parslet run examples/image_filter.py --export-png image_dag.png"
echo ""
echo "5. To stop using the virtual environment (e.g., when you're done working on Parslet), simply type:"
echo "   deactivate"
echo "---------------------------------------------------------------------"

echo ""
echo "✅ Setup script finished."
echo "🎉 Happy Parsleting on Termux!"
echo ""
echo "Please ensure this script was run from the root of the Parslet project directory as stated in prerequisites."
echo "This ensures that the virtual environment is created in the correct location and"
echo "that 'requirements.txt' and 'pip install [-e] .' find the necessary files."
echo ""
echo "If you encounter issues during 'pip install' steps (especially for packages like Pillow, psutil, or pydot),"
echo "double-check that all build dependencies from Step [3/5] were installed correctly."
echo "Consult the Termux wiki or package-specific build instructions for Termux if problems persist."

# End of script

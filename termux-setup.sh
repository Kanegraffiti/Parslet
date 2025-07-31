#!/data/data/com.termux/files/usr/bin/bash
# Lightweight setup script for Termux users
pkg update -y && pkg upgrade -y
pkg install python git graphviz -y
pip install opencv-python numpy pytesseract networkx pillow psutil pydot rich
mkdir -p /storage/emulated/0/Pictures/Diagnostics

#!/bin/bash
# ──────────────────────────────────────────────────────────────
# ACOODA Setup & Run Script
# Adhiyamaan College Online On-Duty Application System
# ──────────────────────────────────────────────────────────────

echo "================================================"
echo " ACOODA - Setup Script"
echo " Adhiyamaan College of Engineering"
echo "================================================"

# Install Python dependencies
echo ""
echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt --break-system-packages --quiet
echo "      ✓ Dependencies installed"

# Create uploads directory
echo ""
echo "[2/4] Creating directories..."
mkdir -p static/uploads
echo "      ✓ Directories ready"

# Database setup instructions
echo ""
echo "[3/4] Database Setup Instructions:"
echo "      Run these MySQL commands:"
echo "      > CREATE DATABASE acooda_db;"
echo "      > CREATE USER 'acooda'@'localhost' IDENTIFIED BY 'password';"
echo "      > GRANT ALL ON acooda_db.* TO 'acooda'@'localhost';"
echo "      Then update config.py SQLALCHEMY_DATABASE_URI"
echo ""
echo "      For SQLite (no MySQL setup needed), update config.py:"
echo "      SQLALCHEMY_DATABASE_URI = 'sqlite:///acooda.db'"

# Run the app
echo ""
echo "[4/4] Starting ACOODA..."
echo ""
echo "  App URL  : http://localhost:5000"
echo "  Admin    : admin@ace.edu / admin123"
echo "  Tutor pw : staff123 (default)"
echo "  HOD pw   : hod123 (default)"
echo ""
echo "================================================"

python app.py

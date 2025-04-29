#!/bin/bash

echo "🚀 Starting Project Setup..."

# Check if .venv exists
if [ ! -d ".venv" ]; then
  echo "🔧 Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate virtual environment
echo "🔗 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Generate model if not already exists
echo "🛠 Running model generation script..."
python3 scripts/generate_model.py

# Start Flask app
echo "🚀 Starting Flask App..."
python3 app.py
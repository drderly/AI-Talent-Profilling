#!/bin/bash

echo "========================================"
echo "  LLM UI - Starting Application"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -d "venv/lib/python*/site-packages/panel" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Check if database exists
if [ ! -f "llm_ui.db" ]; then
    echo "Database not found. Running setup..."
    python setup.py
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
    echo ""
fi

# Start the application
echo "Starting LLM UI..."
echo ""
echo "Application will be available at: http://localhost:5006"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py

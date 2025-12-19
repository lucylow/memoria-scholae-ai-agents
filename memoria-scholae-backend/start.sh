#!/bin/bash

# MemoriaScholae Backend Quick Start Script

echo "=========================================="
echo "MemoriaScholae Backend Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
    echo ""
    echo "Required configuration:"
    echo "  - OPENAI_API_KEY (required)"
    echo "  - NEO4J_PASSWORD (if using Neo4j)"
    echo "  - MEMMACHINE_URL (default: http://localhost:8080)"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Check if MemMachine is running
echo ""
echo "🔍 Checking MemMachine connection..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ MemMachine is running"
else
    echo "⚠️  MemMachine is not running at http://localhost:8080"
    echo "   Start it with: docker run -p 8080:8080 memmachine/memmachine"
fi

# Check if Neo4j is running
echo ""
echo "🔍 Checking Neo4j connection..."
if nc -z localhost 7687 > /dev/null 2>&1; then
    echo "✅ Neo4j is running"
else
    echo "⚠️  Neo4j is not running at localhost:7687"
    echo "   Start it with: docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j"
fi

echo ""
echo "=========================================="
echo "🚀 Starting MemoriaScholae Backend..."
echo "=========================================="
echo ""
echo "API will be available at:"
echo "  - Main API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo ""

# Start the server
python main.py

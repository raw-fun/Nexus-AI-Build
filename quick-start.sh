#!/bin/bash

# NADG Quick Start Script
# This script helps verify your setup and get started quickly

echo "🤖 NEXUS-AI Distributed Grid - Quick Start"
echo "=========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Python 3 found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Check pip
if command_exists pip3; then
    echo "✅ pip3 found"
else
    echo "❌ pip3 not found. Please install pip"
    exit 1
fi

echo ""
echo "📦 Select what you want to set up:"
echo "1. Worker Node (local testing)"
echo "2. Master Orchestrator App"
echo "3. Database Management Tools"
echo "4. Everything"
echo ""
read -p "Enter your choice (1-4): " choice

setup_worker() {
    echo ""
    echo "🔧 Setting up Worker Node..."
    cd worker-node || exit
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    echo ""
    echo "✅ Worker Node setup complete!"
    echo ""
    echo "To start the worker:"
    echo "  cd worker-node"
    echo "  source venv/bin/activate"
    echo "  python main.py"
    echo ""
    echo "To test the worker:"
    echo "  python test_worker.py"
    
    deactivate
}

setup_master() {
    echo ""
    echo "🔧 Setting up Master Orchestrator..."
    cd master-app || exit
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        echo ""
        echo "⚠️  No .env file found. Creating from template..."
        cp .env.example .env
        echo "📝 Please edit master-app/.env with your API keys:"
        echo "   - GEMINI_API_KEY"
        echo "   - SUPABASE_URL"
        echo "   - SUPABASE_SERVICE_KEY"
    fi
    
    echo ""
    echo "✅ Master App setup complete!"
    echo ""
    echo "Before running, make sure to:"
    echo "  1. Edit master-app/.env with your credentials"
    echo "  2. Set up Supabase database (see SETUP_GUIDE.md)"
    echo ""
    echo "To start the master app:"
    echo "  cd master-app"
    echo "  source venv/bin/activate"
    echo "  streamlit run app.py"
    
    deactivate
}

setup_database_tools() {
    echo ""
    echo "🔧 Setting up Database Management Tools..."
    cd database || exit
    
    echo "Installing dependencies..."
    pip3 install -q supabase
    
    echo ""
    echo "✅ Database tools setup complete!"
    echo ""
    echo "To use the worker management tool:"
    echo "  export SUPABASE_URL='your-url'"
    echo "  export SUPABASE_SERVICE_KEY='your-key'"
    echo "  cd database"
    echo "  python manage_workers.py list"
}

case $choice in
    1)
        setup_worker
        ;;
    2)
        setup_master
        ;;
    3)
        setup_database_tools
        ;;
    4)
        setup_worker
        cd ..
        setup_master
        cd ..
        setup_database_tools
        echo ""
        echo "🎉 All components set up successfully!"
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 Next steps:"
echo "  1. Read SETUP_GUIDE.md for detailed instructions"
echo "  2. Configure GitHub Secrets (see README.md)"
echo "  3. Set up Supabase database (see database/schema.sql)"
echo "  4. Deploy workers to Hugging Face Spaces"
echo ""
echo "Happy distributing! 🚀"

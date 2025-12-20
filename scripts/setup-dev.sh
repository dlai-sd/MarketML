#!/bin/bash

# Local development setup script
# Usage: ./scripts/setup-dev.sh

set -e

echo "🛠️  Setting up MarketML development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$PYTHON_VERSION" != "3.11" ]; then
  echo "⚠️  Warning: Python 3.11 recommended, found $PYTHON_VERSION"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Download spaCy model
echo "📦 Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
  echo "📝 Creating .env file..."
  cp .env.example .env
  echo "⚠️  Please update .env with your configuration"
fi

# Create data directory
mkdir -p data/enrichment

# Initialize database
echo "💾 Initializing database..."
python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
print('✅ Database initialized')
"

# Run pre-commit setup
if command -v pre-commit &> /dev/null; then
  echo "🔧 Setting up pre-commit hooks..."
  pre-commit install
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Start services: docker-compose up -d redis qdrant"
echo "3. Run app: uvicorn app.main:app --reload"
echo "4. Run tests: pytest"
echo ""
echo "Or use the quick start script:"
echo "  ./start.sh"

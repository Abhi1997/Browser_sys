#!/bin/bash
# Complete Production Setup Script

set -e

echo "🎯 EduBrowser Production Setup"
echo "=============================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Please do not run this script as root. It will use sudo when needed."
   exit 1
fi

# Step 1: Database Setup
echo "📊 Step 1: Database Setup"
echo "-------------------------"
read -p "Have you set up your MySQL database? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please set up your MySQL database first:"
    echo "1. Create database on db.abhinavpaudel.com (or your database host)"
    echo "2. Create user and grant permissions"
    echo "3. Update .env file with database credentials"
    exit 1
fi

# Step 2: Environment Configuration
echo ""
echo "⚙️  Step 2: Environment Configuration"
echo "--------------------------------------"
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env with your production values:"
    echo "   - DB_HOST, DB_USER, DB_PASSWORD, DB_NAME"
    echo "   - JWT_SECRET (generate a secure random key)"
    echo ""
    read -p "Press Enter after you've edited .env to continue..."
else
    echo "✅ .env file exists"
fi

# Step 3: Python Environment
echo ""
echo "🐍 Step 3: Python Environment"
echo "------------------------------"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Database Initialization
echo ""
echo "🗄️  Step 4: Database Initialization"
echo "-------------------------------------"
read -p "Initialize database schema? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python database/setup_databases.py
    read -p "Populate with sample data? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python database/populate_sample_data.py
    fi
fi

# Step 5: Test Database Connection
echo ""
echo "🔌 Step 5: Testing Database Connection"
echo "--------------------------------------"
python -c "from authentication import Authentication; auth = Authentication(); print('✅ Database connection successful!')" || {
    echo "❌ Database connection failed!"
    echo "Please check your .env configuration and try again."
    exit 1
}

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Test the browser application: python main.py"
echo "2. Verify database connection"
echo "3. Test login with different user roles"
echo "4. Test URL filtering for students"
echo ""
echo "📖 See SETUP_GUIDE.md for detailed instructions"


#!/bin/bash
# Build script for Phone Agent (Linux/macOS)
# Usage: ./build.sh

echo "🔨 Building Phone Agent executable..."
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build the executable
echo "📦 Building executable with PyInstaller..."
pyinstaller phone_agent.spec

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "📍 Application location: ./dist/PhoneAgent.app"
        echo ""
        echo "🚀 To run the application:"
        echo "   open ./dist/PhoneAgent.app"
    else
        # Linux
        echo "📍 Executable location: ./dist/PhoneAgent"
        echo ""
        echo "🚀 To run the application:"
        echo "   ./dist/PhoneAgent"
    fi
    echo ""
else
    echo ""
    echo "❌ Build failed. Please check the error messages above."
    echo ""
    exit 1
fi

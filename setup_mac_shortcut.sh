#!/bin/bash

# Setup script for Mac Smart Garden Starter
# This script helps you create a desktop shortcut for your Mac

echo "🌱 Smart Garden Mac Setup"
echo "========================="
echo ""

# Get Pi IP address
echo "📡 Let's find your Raspberry Pi's IP address..."
echo "Please enter your Raspberry Pi's IP address:"
read -p "IP Address (e.g., 192.168.1.100): " PI_IP

# Get Pi username
echo ""
echo "👤 What username do you use on your Raspberry Pi?"
read -p "Username (default: pi): " PI_USER
PI_USER=${PI_USER:-pi}

echo ""
echo "🔧 Creating Mac application..."

# Create the application bundle
mkdir -p SmartGardenStarter.app/Contents/MacOS
mkdir -p SmartGardenStarter.app/Contents/Resources

# Update the script with user's IP and username
sed "s/YOUR_PI_IP_ADDRESS/$PI_IP/g; s/pi@$PI_IP/$PI_USER@$PI_IP/g" SmartGardenStarter.app/Contents/MacOS/SmartGardenStarter > temp_script
mv temp_script SmartGardenStarter.app/Contents/MacOS/SmartGardenStarter

# Make it executable
chmod +x SmartGardenStarter.app/Contents/MacOS/SmartGardenStarter

# Copy Info.plist
cp SmartGardenStarter.app/Contents/Info.plist SmartGardenStarter.app/Contents/Info.plist

echo "✅ Mac application created!"
echo ""
echo "📋 Next steps:"
echo "1. Copy 'SmartGardenStarter.app' to your Mac"
echo "2. Drag it to your Desktop or Applications folder"
echo "3. Double-click to start your Smart Garden system!"
echo ""
echo "🌐 Your Smart Garden will be available at:"
echo "   http://$PI_IP:3000/presentation"
echo ""
echo "🎯 Perfect for your school presentation!"


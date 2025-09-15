#!/bin/bash

# Smart Garden Quick Start for Mac
# Replace YOUR_PI_IP_ADDRESS with your actual Raspberry Pi IP address

PI_IP="YOUR_PI_IP_ADDRESS"  # Change this to your Pi's IP address
PI_USER="pi"                # Change if you use a different username

echo "🌱 Starting Smart Garden Presentation System..."
echo "📡 Connecting to Raspberry Pi at $PI_IP..."

# Open Terminal and SSH into Pi to start the system
osascript -e "tell application \"Terminal\" to activate"
osascript -e "tell application \"Terminal\" to do script \"echo '🌱 Smart Garden System Starting...' && ssh $PI_USER@$PI_IP 'cd /home/pi/smart-garden-backend-master && ./quick_start.sh'\""

echo "✅ Smart Garden system is starting on your Raspberry Pi!"
echo "🌐 Open your browser and go to: http://$PI_IP:3000/presentation"
echo "📱 Or scan the QR code that will appear in the terminal"


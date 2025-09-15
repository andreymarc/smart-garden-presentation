-- Smart Garden Quick Start for Mac
-- This script will SSH into your Raspberry Pi and start the smart garden system

tell application "Terminal"
    activate
    do script "echo '🌱 Starting Smart Garden Presentation System...' && echo 'Connecting to Raspberry Pi...' && ssh pi@YOUR_PI_IP_ADDRESS 'cd /home/pi/smart-garden-backend-master && ./quick_start.sh'"
end tell


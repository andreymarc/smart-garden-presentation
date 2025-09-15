#!/bin/bash

# Ultra Quick Start - One Command Launch
# For presentation day - just run this!

echo "⚡ ULTRA QUICK START - AeroStream Presentation"
echo "==============================================="

cd /home/pi/smart-garden-backend-master

# Kill everything first
pkill -f "node server.js" 2>/dev/null
pkill -f "python3.*sensor" 2>/dev/null
sleep 1

# Start everything
echo "🚀 Launching system..."
node server.js &
python3 simple_accurate_sensor.py &

sleep 5

echo ""
echo "🎉 READY FOR PRESENTATION!"
echo "=========================="
echo "📊 Open: http://localhost:3000/presentation"
echo "📱 Network: http://$(hostname -I | awk '{print $1}'):3000/presentation"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Keep script running and show status
while true; do
    sleep 10
    if curl -s http://localhost:3000/api/sensors > /dev/null; then
        echo "✅ System running - $(date '+%H:%M:%S')"
    else
        echo "❌ System not responding - $(date '+%H:%M:%S')"
    fi
done


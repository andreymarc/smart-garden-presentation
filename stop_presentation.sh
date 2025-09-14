#!/bin/bash

# Smart Garden Presentation Stop Script
# Quick and easy shutdown

echo "🛑 Stopping Smart Garden Presentation System..."
echo "=============================================="

# Change to the correct directory
cd /home/pi/smart-garden-backend-master

# Stop processes using saved PIDs
if [ -f .server_pid ]; then
    SERVER_PID=$(cat .server_pid)
    if ps -p $SERVER_PID > /dev/null; then
        echo "🔄 Stopping web server (PID: $SERVER_PID)..."
        kill $SERVER_PID
    fi
    rm .server_pid
fi

if [ -f .sensor_pid ]; then
    SENSOR_PID=$(cat .sensor_pid)
    if ps -p $SENSOR_PID > /dev/null; then
        echo "🔄 Stopping sensors (PID: $SENSOR_PID)..."
        kill $SENSOR_PID
    fi
    rm .sensor_pid
fi

# Kill any remaining processes
echo "🔄 Cleaning up any remaining processes..."
pkill -f "node server.js" 2>/dev/null
pkill -f "python3.*sensor" 2>/dev/null

sleep 2

echo "✅ All systems stopped!"
echo "🎯 Ready for next presentation!"
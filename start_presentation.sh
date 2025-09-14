#!/bin/bash

# Smart Garden Presentation Startup Script
# Quick and easy startup for presentation day

echo "🚀 Starting Smart Garden Presentation System..."
echo "=============================================="

# Change to the correct directory
cd /home/pi/smart-garden-backend-master

# Kill any existing processes
echo "🔄 Stopping any existing processes..."
pkill -f "node server.js" 2>/dev/null
pkill -f "python3.*sensor" 2>/dev/null
sleep 2

# Start the Node.js server
echo "🌐 Starting web server..."
node server.js &
SERVER_PID=$!
sleep 3

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Web server started successfully (PID: $SERVER_PID)"
else
    echo "❌ Failed to start web server"
    exit 1
fi

# Start the real sensors
echo "🌡️ Starting real sensors..."
python3 real_sensors_only.py &
SENSOR_PID=$!
sleep 2

# Check if sensors started successfully
if ps -p $SENSOR_PID > /dev/null; then
    echo "✅ Real sensors started successfully (PID: $SENSOR_PID)"
else
    echo "❌ Failed to start sensors"
    exit 1
fi

# Wait a moment for data to start flowing
echo "⏳ Waiting for sensor data..."
sleep 5

# Test the system
echo "🧪 Testing the system..."
if curl -s http://localhost:3000/api/sensors > /dev/null; then
    echo "✅ API is responding"
else
    echo "❌ API not responding"
fi

# Display status
echo ""
echo "🎉 PRESENTATION SYSTEM READY!"
echo "=============================="
echo "📊 Dashboard: http://localhost:3000/presentation"
echo "🔬 Real Sensors: http://localhost:3000/real-sensors"
echo "🏫 School Mode: http://localhost:3000/school"
echo ""
echo "📱 Access from any device on the same network:"
echo "   http://$(hostname -I | awk '{print $1}'):3000/presentation"
echo ""
echo "🛑 To stop the system, run: ./stop_presentation.sh"
echo ""

# Save PIDs for easy stopping
echo $SERVER_PID > .server_pid
echo $SENSOR_PID > .sensor_pid

echo "✅ System is running! Ready for your presentation!"
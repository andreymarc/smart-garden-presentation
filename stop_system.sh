#!/bin/bash

echo "🛑 Stopping Smart Garden Air Quality Monitoring System..."
echo "=================================================="

# Stop all related processes
echo "🔄 Stopping processes..."

# Stop backend server
pkill -f "node server.js"
if [ $? -eq 0 ]; then
    echo "✅ Backend server stopped"
else
    echo "⚠️  Backend server was not running"
fi

# Stop frontend
pkill -f "react-scripts start"
if [ $? -eq 0 ]; then
    echo "✅ Frontend stopped"
else
    echo "⚠️  Frontend was not running"
fi

# Stop sensor simulation
pkill -f "simulate_sensor.py"
if [ $? -eq 0 ]; then
    echo "✅ Sensor simulation stopped"
else
    echo "⚠️  Sensor simulation was not running"
fi

# Wait a moment for processes to stop
sleep 2

echo ""
echo "🎉 All processes stopped successfully!"
echo "==================================================" 
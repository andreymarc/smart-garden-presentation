#!/bin/bash

echo "🎭 Starting Air Quality Monitoring Demo for Presentation..."
echo "========================================================"

# Check if we're in the right directory
if [ ! -f "server.js" ]; then
    echo "❌ Error: Please run this script from the smart-garden-backend directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Kill existing processes if they exist
echo "🔄 Stopping existing processes..."
pkill -f "node server.js" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null
pkill -f "demo_sensor.py" 2>/dev/null
pkill -f "simulate_sensor.py" 2>/dev/null

sleep 2

# Start the backend server
echo "🚀 Starting backend server..."
if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Backend might already be running."
else
    nohup node server.js > server.log 2>&1 &
    echo "✅ Backend server started (PID: $!)"
fi

# Wait a moment for the server to start
sleep 3

# Start the frontend
echo "🎨 Starting frontend..."
cd frontend
if check_port 3001; then
    echo "⚠️  Port 3001 is already in use. Frontend might already be running."
else
    nohup npm start > ../frontend.log 2>&1 &
    echo "✅ Frontend started (PID: $!)"
fi
cd ..

# Wait a moment for the frontend to start
sleep 5

# Start the demo sensor simulation
echo "📡 Starting demo sensor simulation..."
nohup python3 demo_sensor.py > demo.log 2>&1 &
echo "✅ Demo sensor simulation started (PID: $!)"

echo ""
echo "🎉 Demo System is now running!"
echo "========================================================"
echo "📊 Backend API: http://localhost:3000"
echo "🌐 Frontend: http://localhost:3001"
echo "📡 Demo scenarios: Changing every 2 minutes"
echo ""
echo "🎭 Demo Scenarios:"
echo "   1. 🌤️  Normal Conditions"
echo "   2. 🔥 High Temperature Alert"
echo "   3. 💧 High Humidity Alert"
echo "   4. 💨 Poor Air Quality Alert"
echo "   5. 🌪️  Pressure Change Alert"
echo "   6. ⚡ Multiple Alerts"
echo "   7. 🌡️  Temperature Fluctuation"
echo "   8. 🔄 Recovery Scenario"
echo ""
echo "📋 Log files:"
echo "   - Backend: server.log"
echo "   - Frontend: frontend.log"
echo "   - Demo: demo.log"
echo ""
echo "📸 Perfect for screenshots!"
echo "🛑 To stop the demo, run: ./stop_system.sh"
echo "========================================================" 
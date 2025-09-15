#!/bin/bash

echo "🏫 Starting Smart School Air Quality Monitor!"
echo "=============================================="

# Kill any existing processes
echo "🔄 Stopping existing processes..."
pkill -f "node server.js" 2>/dev/null
pkill -f "enviro_led_gpio.py" 2>/dev/null
pkill -f "simple_lcd_display.py" 2>/dev/null
pkill -f "enviro_all_sensors.py" 2>/dev/null
pkill -f "school_smart_alerts.py" 2>/dev/null
pkill -f "simulate_sensor.py" 2>/dev/null

sleep 2

# Start the backend server
echo "🚀 Starting backend server..."
nohup node server.js > server.log 2>&1 &
echo "✅ Backend server started"

sleep 3

# Start the frontend
echo "🎨 Starting frontend..."
cd frontend
PORT=3001 nohup npm start > ../frontend.log 2>&1 &
cd ..
echo "✅ Frontend started"

sleep 5

# Start all sensors
echo "📡 Starting all Enviro+ sensors..."
nohup python3 enviro_all_sensors.py > all_sensors.log 2>&1 &
echo "✅ All sensors started"

# Start LCD display
echo "📱 Starting LCD display..."
nohup python3 simple_lcd_display.py > lcd_display.log 2>&1 &
echo "✅ LCD display started"

# Start LED control
echo "💡 Starting LED control..."
nohup python3 enviro_led_gpio.py > led_control.log 2>&1 &
echo "✅ LED control started"

# Start school smart alerts
echo "🎓 Starting school smart alerts..."
nohup python3 school_smart_alerts.py > school_alerts.log 2>&1 &
echo "✅ School smart alerts started"

echo ""
echo "🎉 SCHOOL MODE READY!"
echo "=============================================="
echo "🏫 School Dashboard: http://localhost:3000/school"
echo "🌟 Main Dashboard: http://localhost:3001"
echo "🎭 General Presentation: http://localhost:3000/presentation"
echo "📊 Display Control: http://localhost:3000/display-control"
echo ""
echo "📋 All systems running:"
echo "   ✅ Backend API (Port 3000)"
echo "   ✅ Frontend Dashboard (Port 3001)"
echo "   ✅ All Enviro+ Sensors"
echo "   ✅ LCD Display"
echo "   ✅ LED Control"
echo "   ✅ School Smart Alerts"
echo ""
echo "🎯 For your school presentation, use:"
echo "   http://localhost:3000/school"
echo ""
echo "💡 Smart Features:"
echo "   🌡️ Temperature alerts (AC recommendations)"
echo "   💨 Air quality alerts (ventilation recommendations)"
echo "   💧 Humidity monitoring (comfort optimization)"
echo "   📚 Educational tips for students"
echo "   🚨 Real-time alerts for teachers"
echo ""
echo "🛑 To stop everything: ./stop_presentation.sh"
echo "=============================================="




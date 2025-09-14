#!/bin/bash

echo "📺 Watching Demo Logs..."
echo "Press Ctrl+C to stop watching"
echo "================================"

# Function to show demo status
show_status() {
    echo ""
    echo "🎭 Current Demo Status:"
    echo "========================"
    
    # Check if processes are running
    if pgrep -f "demo_sensor.py" > /dev/null; then
        echo "✅ Demo sensor: Running"
    else
        echo "❌ Demo sensor: Not running"
    fi
    
    if pgrep -f "node server.js" > /dev/null; then
        echo "✅ Backend server: Running"
    else
        echo "❌ Backend server: Not running"
    fi
    
    if pgrep -f "react-scripts" > /dev/null; then
        echo "✅ Frontend: Running"
    else
        echo "❌ Frontend: Not running"
    fi
    
    echo ""
    echo "📊 Latest sensor data:"
    curl -s http://localhost:3000/api/sensors | tail -1 | python3 -m json.tool 2>/dev/null || echo "No data available"
    
    echo ""
    echo "📋 Demo scenarios:"
    echo "   1. 🌤️  Normal Conditions"
    echo "   2. 🔥 High Temperature Alert"
    echo "   3. 💧 High Humidity Alert"
    echo "   4. 💨 Poor Air Quality Alert"
    echo "   5. 🌪️  Pressure Change Alert"
    echo "   6. ⚡ Multiple Alerts"
    echo "   7. 🌡️  Temperature Fluctuation"
    echo "   8. 🔄 Recovery Scenario"
    echo ""
    echo "🌐 Frontend: http://localhost:3001"
    echo "📊 API: http://localhost:3000/api/sensors"
    echo "================================"
}

# Show initial status
show_status

# Watch demo logs in real-time
echo "📺 Watching demo logs (Ctrl+C to stop):"
echo "================================"

tail -f demo.log 
#!/usr/bin/env python3
"""
Smart School Air Quality Alerts
Provides intelligent recommendations for schools based on air quality data
"""

import time
import sys
import requests
import random
from datetime import datetime

def get_school_recommendations(sensor_data):
    """Generate smart recommendations for school environment"""
    recommendations = []
    alerts = []
    
    temp = sensor_data.get('temperature', 20) or 20
    humidity = sensor_data.get('humidity', 50) or 50
    gas = sensor_data.get('gas', 200000) or 200000
    pressure = sensor_data.get('pressure', 1013) or 1013
    aqi = sensor_data.get('aqi', 50) or 50
    
    # Temperature recommendations
    if temp > 28:
        recommendations.append({
            'type': 'temperature',
            'priority': 'high',
            'title': '🌡️ Temperature Too High',
            'message': f'Classroom temperature is {temp:.1f}°C - above comfortable learning range',
            'action': 'Turn on AC or increase ventilation',
            'details': 'Optimal learning temperature is 20-25°C. High temperatures can reduce concentration and learning effectiveness.',
            'icon': '🌡️'
        })
        alerts.append('HOT_TEMP')
    elif temp < 18:
        recommendations.append({
            'type': 'temperature',
            'priority': 'medium',
            'title': '❄️ Temperature Too Low',
            'message': f'Classroom temperature is {temp:.1f}°C - below comfortable range',
            'action': 'Turn on heating system',
            'details': 'Cold temperatures can make students uncomfortable and reduce focus.',
            'icon': '❄️'
        })
        alerts.append('COLD_TEMP')
    else:
        recommendations.append({
            'type': 'temperature',
            'priority': 'low',
            'title': '✅ Temperature Optimal',
            'message': f'Classroom temperature is {temp:.1f}°C - perfect for learning!',
            'action': 'Maintain current settings',
            'details': 'Temperature is in the optimal range for student comfort and concentration.',
            'icon': '✅'
        })
    
    # Humidity recommendations
    if humidity > 70:
        recommendations.append({
            'type': 'humidity',
            'priority': 'medium',
            'title': '💧 Humidity Too High',
            'message': f'Humidity is {humidity:.1f}% - too humid for comfort',
            'action': 'Turn on AC or dehumidifier',
            'details': 'High humidity can cause mold growth and make the air feel stuffy. Students may feel uncomfortable.',
            'icon': '💧'
        })
        alerts.append('HIGH_HUMIDITY')
    elif humidity < 30:
        recommendations.append({
            'type': 'humidity',
            'priority': 'medium',
            'title': '🏜️ Air Too Dry',
            'message': f'Humidity is {humidity:.1f}% - air is too dry',
            'action': 'Use humidifier or open windows',
            'details': 'Dry air can cause dry skin, irritated eyes, and respiratory discomfort.',
            'icon': '🏜️'
        })
        alerts.append('LOW_HUMIDITY')
    else:
        recommendations.append({
            'type': 'humidity',
            'priority': 'low',
            'title': '✅ Humidity Perfect',
            'message': f'Humidity is {humidity:.1f}% - ideal for learning',
            'action': 'Maintain current settings',
            'details': 'Humidity is in the optimal range for student comfort and health.',
            'icon': '✅'
        })
    
    # Air Quality recommendations
    if aqi > 150:
        recommendations.append({
            'type': 'air_quality',
            'priority': 'high',
            'title': '🚨 Poor Air Quality',
            'message': f'Air Quality Index is {aqi} - unhealthy for students',
            'action': 'Open windows, turn on air purifier, or check ventilation system',
            'details': 'Poor air quality can cause headaches, fatigue, and respiratory issues. Students with asthma may be particularly affected.',
            'icon': '🚨'
        })
        alerts.append('POOR_AIR')
    elif aqi > 100:
        recommendations.append({
            'type': 'air_quality',
            'priority': 'medium',
            'title': '⚠️ Moderate Air Quality',
            'message': f'Air Quality Index is {aqi} - sensitive students may be affected',
            'action': 'Improve ventilation or use air purifier',
            'details': 'Students with allergies or respiratory conditions may experience mild discomfort.',
            'icon': '⚠️'
        })
        alerts.append('MODERATE_AIR')
    else:
        recommendations.append({
            'type': 'air_quality',
            'priority': 'low',
            'title': '✅ Excellent Air Quality',
            'message': f'Air Quality Index is {aqi} - perfect for learning!',
            'action': 'Maintain current ventilation',
            'details': 'Air quality is excellent for student health and concentration.',
            'icon': '✅'
        })
    
    # Gas sensor recommendations
    if gas < 100000:
        recommendations.append({
            'type': 'gas',
            'priority': 'high',
            'title': '💨 High Gas Levels Detected',
            'message': f'Gas resistance is {gas/1000:.1f}kΩ - air may be contaminated',
            'action': 'Immediately ventilate the room and check for sources',
            'details': 'High gas levels could indicate chemical exposure, cleaning products, or other contaminants. Ensure proper ventilation.',
            'icon': '💨'
        })
        alerts.append('HIGH_GAS')
    
    # Pressure recommendations (weather-related)
    if pressure < 980:
        recommendations.append({
            'type': 'pressure',
            'priority': 'low',
            'title': '🌧️ Low Pressure - Weather Change',
            'message': f'Atmospheric pressure is {pressure:.1f} hPa - stormy weather expected',
            'action': 'Monitor weather and prepare for indoor activities',
            'details': 'Low pressure often indicates approaching storms. Students may feel more tired or have headaches.',
            'icon': '🌧️'
        })
    elif pressure > 1020:
        recommendations.append({
            'type': 'pressure',
            'priority': 'low',
            'title': '☀️ High Pressure - Clear Weather',
            'message': f'Atmospheric pressure is {pressure:.1f} hPa - clear weather conditions',
            'action': 'Great weather for outdoor activities!',
            'details': 'High pressure indicates clear, stable weather. Perfect for outdoor learning activities.',
            'icon': '☀️'
        })
    
    return recommendations, alerts

def get_educational_tips():
    """Get educational tips about air quality for students"""
    tips = [
        "🌱 Plants help clean the air by absorbing carbon dioxide and releasing oxygen",
        "💨 Opening windows for 10 minutes can significantly improve air quality",
        "🌡️ The ideal classroom temperature is 20-25°C for optimal learning",
        "💧 Humidity between 40-60% is most comfortable for students",
        "🚫 Avoid using strong cleaning products during school hours",
        "🌿 Some plants like spider plants and peace lilies are great air purifiers",
        "📚 Poor air quality can reduce student concentration by up to 20%",
        "🏫 Schools with good air quality have 15% fewer sick days"
    ]
    return random.choice(tips)

def send_school_alerts(recommendations, alerts):
    """Send alerts to school administration"""
    if not alerts:
        return
    
    alert_message = "🚨 School Air Quality Alert!\n\n"
    
    for rec in recommendations:
        if rec['priority'] == 'high':
            alert_message += f"{rec['icon']} {rec['title']}\n"
            alert_message += f"Action: {rec['action']}\n\n"
    
    print("📧 School Alert Generated:")
    print(alert_message)
    
    # Here you could integrate with email, SMS, or school notification systems
    return alert_message

def main():
    """Main function for school smart alerts"""
    print("🏫 School Smart Air Quality Alerts")
    print("=" * 50)
    
    try:
        while True:
            # Get current sensor data
            try:
                response = requests.get('http://localhost:3000/api/sensors')
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        sensor_data = data[0]
                    else:
                        # Use mock data if no real data
                        sensor_data = {
                            'temperature': random.uniform(15, 35),
                            'humidity': random.uniform(20, 80),
                            'gas': random.uniform(50000, 400000),
                            'pressure': random.uniform(970, 1030),
                            'aqi': random.uniform(0, 300)
                        }
                else:
                    # Use mock data
                    sensor_data = {
                        'temperature': random.uniform(15, 35),
                        'humidity': random.uniform(20, 80),
                        'gas': random.uniform(50000, 400000),
                        'pressure': random.uniform(970, 1030),
                        'aqi': random.uniform(0, 300)
                    }
            except:
                # Use mock data
                sensor_data = {
                    'temperature': random.uniform(15, 35),
                    'humidity': random.uniform(20, 80),
                    'gas': random.uniform(50000, 400000),
                    'pressure': random.uniform(970, 1030),
                    'aqi': random.uniform(0, 300)
                }
            
            # Generate recommendations
            recommendations, alerts = get_school_recommendations(sensor_data)
            
            # Display current status
            print(f"\n📊 Classroom Environment - {datetime.now().strftime('%H:%M:%S')}")
            print(f"🌡️ Temperature: {sensor_data.get('temperature', 0):.1f}°C")
            print(f"💧 Humidity: {sensor_data.get('humidity', 0):.1f}%")
            print(f"🌪️ Pressure: {sensor_data.get('pressure', 0):.1f} hPa")
            print(f"💨 Gas: {sensor_data.get('gas', 0)/1000:.1f}kΩ")
            print(f"📊 AQI: {sensor_data.get('aqi', 0):.0f}")
            
            # Display recommendations
            print(f"\n🎯 Smart Recommendations:")
            for rec in recommendations:
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                print(f"{priority_icon} {rec['title']}")
                print(f"   Action: {rec['action']}")
                print(f"   Details: {rec['details']}")
                print()
            
            # Send alerts if needed
            if alerts:
                send_school_alerts(recommendations, alerts)
            
            # Show educational tip
            tip = get_educational_tips()
            print(f"💡 Educational Tip: {tip}")
            
            # Wait before next check
            print(f"\n⏱️ Next check in 30 seconds...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping school alerts...")
        print("✅ School alert system stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

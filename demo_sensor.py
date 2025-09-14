#!/usr/bin/env python3
"""
Advanced Demo Sensor for Air Quality Monitoring System
Creates interesting scenarios for presentation
"""

import time
import json
import random
import requests
from datetime import datetime
import math

class DemoScenario:
    def __init__(self):
        self.scenario = 0
        self.time_in_scenario = 0
        self.base_temp = 22.0
        self.base_humidity = 45.0
        self.base_pressure = 1013.25
        self.base_gas = 250000
        
    def get_scenario_name(self):
        scenarios = [
            "🌤️  Normal Conditions",
            "🔥 High Temperature Alert",
            "💧 High Humidity Alert", 
            "💨 Poor Air Quality Alert",
            "🌪️  Pressure Change Alert",
            "⚡ Multiple Alerts",
            "🌡️  Temperature Fluctuation",
            "🔄 Recovery Scenario"
        ]
        return scenarios[self.scenario % len(scenarios)]
    
    def generate_scenario_data(self):
        """Generate data based on current scenario"""
        self.time_in_scenario += 1
        
        # Change scenario every 2 minutes (4 readings)
        if self.time_in_scenario >= 4:
            self.scenario += 1
            self.time_in_scenario = 0
            print(f"\n🔄 Switching to scenario: {self.get_scenario_name()}")
        
        scenario = self.scenario % 8
        
        if scenario == 0:  # Normal conditions
            temp = self.base_temp + random.uniform(-1, 1)
            humidity = self.base_humidity + random.uniform(-5, 5)
            gas = self.base_gas + random.uniform(-20000, 20000)
            pressure = self.base_pressure + random.uniform(-5, 5)
            
        elif scenario == 1:  # High temperature
            temp = 32 + random.uniform(-1, 2)
            humidity = self.base_humidity + random.uniform(-5, 5)
            gas = self.base_gas + random.uniform(-20000, 20000)
            pressure = self.base_pressure + random.uniform(-5, 5)
            
        elif scenario == 2:  # High humidity
            temp = self.base_temp + random.uniform(-1, 1)
            humidity = 75 + random.uniform(-3, 5)
            gas = self.base_gas + random.uniform(-20000, 20000)
            pressure = self.base_pressure + random.uniform(-5, 5)
            
        elif scenario == 3:  # Poor air quality
            temp = self.base_temp + random.uniform(-1, 1)
            humidity = self.base_humidity + random.uniform(-5, 5)
            gas = 80000 + random.uniform(-10000, 10000)  # Low resistance = bad air
            pressure = self.base_pressure + random.uniform(-5, 5)
            
        elif scenario == 4:  # Pressure change
            temp = self.base_temp + random.uniform(-1, 1)
            humidity = self.base_humidity + random.uniform(-5, 5)
            gas = self.base_gas + random.uniform(-20000, 20000)
            pressure = 965 + random.uniform(-3, 3)  # Low pressure
            
        elif scenario == 5:  # Multiple alerts
            temp = 35 + random.uniform(-1, 2)  # High temp
            humidity = 80 + random.uniform(-3, 5)  # High humidity
            gas = 60000 + random.uniform(-10000, 10000)  # Bad air
            pressure = 970 + random.uniform(-3, 3)  # Low pressure
            
        elif scenario == 6:  # Temperature fluctuation
            # Create a wave pattern
            wave = math.sin(self.time_in_scenario * 0.5) * 8
            temp = self.base_temp + wave + random.uniform(-0.5, 0.5)
            humidity = self.base_humidity + random.uniform(-5, 5)
            gas = self.base_gas + random.uniform(-20000, 20000)
            pressure = self.base_pressure + random.uniform(-5, 5)
            
        else:  # Recovery scenario
            temp = self.base_temp + random.uniform(-0.5, 0.5)
            humidity = self.base_humidity + random.uniform(-2, 2)
            gas = self.base_gas + random.uniform(-10000, 10000)
            pressure = self.base_pressure + random.uniform(-2, 2)
        
        # Ensure values are within reasonable bounds
        temp = max(15, min(40, temp))
        humidity = max(20, min(95, humidity))
        gas = max(50000, min(500000, gas))
        pressure = max(950, min(1050, pressure))
        
        return {
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'pressure': round(pressure, 2),
            'gas': round(gas),
            'reducing': round(gas * 0.6 + random.uniform(-10000, 10000)),
            'nh3': round(gas * 0.3 + random.uniform(-5000, 5000)),
            'timestamp': datetime.now().isoformat()
        }

def send_to_server(data):
    """Send sensor data to the local server"""
    try:
        url = 'http://localhost:3000/api/sensors'
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 201:
            return True
        else:
            print(f"❌ Failed to send data. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending data: {e}")
        return False

def calculate_aqi(gas):
    """Calculate Air Quality Index"""
    gas_concentration = (1000000 / gas) * 100
    aqi = min(max(gas_concentration * 5, 0), 500)
    return round(aqi)

def get_aqi_status(aqi):
    """Get AQI status and color"""
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "🟠"
    elif aqi <= 200:
        return "Unhealthy", "🔴"
    elif aqi <= 300:
        return "Very Unhealthy", "🟣"
    else:
        return "Hazardous", "🟤"

def main():
    """Main demo function"""
    print("🎭 Starting Advanced Air Quality Demo...")
    print("📡 Sending data to http://localhost:3000/api/sensors")
    print("⏰ Sending data every 30 seconds")
    print("🔄 Scenarios change every 2 minutes")
    print("🛑 Press Ctrl+C to stop\n")
    
    scenario = DemoScenario()
    
    try:
        while True:
            # Generate scenario-based sensor data
            sensor_data = scenario.generate_scenario_data()
            
            # Send to server
            success = send_to_server(sensor_data)
            
            if success:
                # Calculate AQI
                aqi = calculate_aqi(sensor_data['gas'])
                aqi_status, aqi_emoji = get_aqi_status(aqi)
                
                # Print formatted output
                print(f"📊 {scenario.get_scenario_name()}")
                print(f"   🌡️  {sensor_data['temperature']}°C | "
                      f"💧 {sensor_data['humidity']}% | "
                      f"🌪️  {sensor_data['pressure']} hPa | "
                      f"💨 {sensor_data['gas']:,} Ω")
                print(f"   {aqi_emoji} AQI: {aqi} ({aqi_status})")
                print(f"   ⏰ {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 60)
            
            # Wait 30 seconds before next reading
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 
# 🌱 Smart Garden Presentation System

> **Real-time environmental monitoring with interactive dashboard for educational presentations**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/andreymarc/smart-garden-presentation)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Enviro%2B-red?style=for-the-badge&logo=raspberry-pi)](https://shop.pimoroni.com/products/enviro-plus)
[![Node.js](https://img.shields.io/badge/Node.js-Backend-green?style=for-the-badge&logo=node.js)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-Frontend-blue?style=for-the-badge&logo=react)](https://reactjs.org/)

## 🎯 Overview

This project creates a **beautiful, interactive presentation system** for monitoring environmental conditions using real sensors. Perfect for **school presentations**, **educational demonstrations**, and **smart building management**.

### ✨ Key Features

- 🌡️ **Real-time sensor monitoring** (Temperature, Humidity, Pressure, Light)
- 📊 **Interactive charts** with live data visualization
- 🔔 **Smart notifications** with educational insights
- 🎨 **Professional UI** with Font Awesome icons
- 📱 **Responsive design** works on any device
- ⚡ **One-click startup** for easy presentation setup
- 🎓 **School-focused alerts** and recommendations

## 🛠️ Hardware Requirements

### Required Components
- **Raspberry Pi** (3B+, 4B, or newer)
- **Pimoroni Enviro+** environmental sensor board
- **MicroSD card** (32GB+ recommended)
- **Power supply** for Raspberry Pi
- **Optional**: External RGB LED for visual feedback

### Enviro+ Sensors
- **BME280**: Temperature, Humidity, Pressure
- **Light Sensor**: Ambient light detection
- **Gas Sensor**: Air quality monitoring (simulated)
- **MEMS Microphone**: Noise level detection (simulated)
- **0.96" LCD**: Temperature display

## 🚀 Quick Start (Presentation Day)

### Option 1: Desktop Shortcut (Easiest)
1. **Double-click** the desktop icon: `Start Smart Garden Presentation`
2. **Wait** for the system to start (about 30 seconds)
3. **Open browser** and go to: `http://localhost:3000/presentation`
4. **Enjoy** your interactive presentation!

### Option 2: Command Line
```bash
# Navigate to project directory
cd /home/pi/smart-garden-backend-master

# Start the system
./quick_start.sh

# Open in browser
# http://localhost:3000/presentation
```

## 📋 Full Installation Guide

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Enable I2C and SPI interfaces
sudo raspi-config
# Navigate to: Interfacing Options → I2C → Enable
# Navigate to: Interfacing Options → SPI → Enable
# Reboot when prompted
```

### 2. Install Dependencies

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python packages
sudo apt install python3-pip python3-venv -y
pip3 install smbus2 bme280 enviroplus pimoroni-bme280 --break-system-packages

# Install audio libraries (for microphone)
sudo apt install libportaudio2 portaudio19-dev python3-pyaudio -y

# Install SQLite
sudo apt install sqlite3 -y
```

### 3. Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/andreymarc/smart-garden-presentation.git
cd smart-garden-presentation

# Install backend dependencies
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Make scripts executable
chmod +x *.sh
```

### 4. Start the System

```bash
# Quick start (recommended for presentations)
./quick_start.sh

# Or start individual components
npm start                    # Backend server
cd frontend && npm start     # Frontend (port 3001)
python3 real_sensors_only.py # Real sensor data
```

## 🎮 How to Use

### Main Dashboard
- **URL**: `http://localhost:3000/presentation`
- **Features**: Real-time charts, sensor data, smart notifications
- **Interactive**: Click notification header to expand/collapse

### Available Endpoints
- **Presentation**: `http://localhost:3000/presentation`
- **School Mode**: `http://localhost:3000/school`
- **LED Control**: `http://localhost:3000/led-status`
- **Display Control**: `http://localhost:3000/display-control`
- **API**: `http://localhost:3000/api/sensors`

### Smart Notifications
The system provides educational insights:
- 🌡️ **Temperature alerts**: "Perfect for learning!" or "Consider AC"
- 💧 **Humidity monitoring**: "Ideal humidity for comfort"
- 🌬️ **Air quality**: "Fresh air detected" or "Ventilation needed"
- 💡 **Light conditions**: "Good lighting for reading"

## 📊 Sensor Data

### Real Sensors (Live Data)
- **Temperature**: BME280 sensor (-40°C to +85°C)
- **Humidity**: BME280 sensor (0-100% RH)
- **Pressure**: BME280 sensor (300-1100 hPa)
- **Light**: Ambient light sensor (0-65535 lux)

### Simulated Sensors
- **Gas/Air Quality**: Realistic simulation for demonstration
- **Noise Level**: Simulated for educational purposes

## 🎓 Educational Applications

### For Schools
- **Science Classes**: Environmental monitoring, data analysis
- **Technology Education**: IoT, sensors, programming
- **Health & Safety**: Indoor air quality awareness
- **Data Visualization**: Charts, graphs, real-time updates

### Smart Recommendations
- **Temperature**: "Turn on AC if too hot"
- **Air Quality**: "Open windows for fresh air"
- **Lighting**: "Adjust blinds for better reading"
- **Humidity**: "Use dehumidifier if needed"

## 🛠️ Development

### Project Structure
```
smart-garden-presentation/
├── server.js                 # Backend API server
├── presentation.html         # Main presentation dashboard
├── quick_start.sh           # One-click startup script
├── real_sensors_only.py     # Real sensor data collection
├── school_smart_alerts.py   # Educational notifications
├── frontend/                # React frontend
│   ├── src/App.js          # Main React component
│   └── package.json        # Frontend dependencies
└── README.md               # This file
```

### API Endpoints
- `GET /api/sensors` - Get current sensor data
- `POST /api/led/control` - Control LED status
- `POST /api/lcd/control` - Control LCD display
- `POST /api/sensors/control` - Start/stop sensor collection

## 🎯 Presentation Tips

### For Teachers
1. **Start with the dashboard** - Show real-time data
2. **Explain sensors** - Use tooltips for technical details
3. **Demonstrate interactivity** - Click notifications to expand
4. **Show practical applications** - School environment monitoring
5. **Discuss data analysis** - Charts and trends

### Demo Script
1. **"This is our Smart Garden system"** - Show dashboard
2. **"Real sensors are monitoring..."** - Point to sensor cards
3. **"The system provides smart alerts"** - Click notifications
4. **"Perfect for schools because..."** - Show educational value
5. **"Let's see the data in action"** - Breathe on temperature sensor

## 🔧 Troubleshooting

### Common Issues

**Sensors not working:**
```bash
# Check I2C is enabled
sudo raspi-config
# Enable I2C interface

# Test sensor connection
python3 simple_real_sensor.py
```

**Port conflicts:**
```bash
# Kill existing processes
pkill -f node
pkill -f python3

# Check what's using port 3000
lsof -i :3000
```

**Permission errors:**
```bash
# Make scripts executable
chmod +x *.sh

# Run with proper permissions
sudo python3 real_sensors_only.py
```

## 📈 Future Enhancements

- [ ] **Mobile app** for remote monitoring
- [ ] **Historical data** storage and analysis
- [ ] **Email/SMS alerts** for critical conditions
- [ ] **Multi-room monitoring** with multiple sensors
- [ ] **Integration** with smart home systems
- [ ] **Machine learning** for predictive alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Andrey Marc** - [GitHub](https://github.com/andreymarc)

## 🙏 Acknowledgments

- **Pimoroni** for the excellent Enviro+ sensor board
- **Raspberry Pi Foundation** for the amazing platform
- **Node.js and React** communities for the great tools
- **Teachers and students** for the inspiration

---

## 🎉 Ready for Your Presentation!

**Quick Start Command:**
```bash
./quick_start.sh
```

**Dashboard URL:**
```
http://localhost:3000/presentation
```

**Good luck with your presentation!** 🌟

---

*Made with ❤️ for educational purposes*
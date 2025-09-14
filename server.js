const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const { mqtt, io, iot } = require('aws-iot-device-sdk-v2');
const cron = require('node-cron');

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

let sensorData = [];
let scheduledNotifications = [];

// Local SQLite Database connection
const db = new sqlite3.Database('./air_quality.db', (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
    } else {
        console.log('Connected to the local SQLite database.');
        // Create table if it doesn't exist
        db.run(`CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            temperature REAL,
            humidity REAL,
            pressure REAL,
            gas REAL,
            reducing REAL,
            nh3 REAL,
            aqi REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`, (err) => {
            if (err) {
                console.error('Error creating table:', err.message);
            } else {
                console.log('Sensor data table created successfully');
            }
        });

        // Create index for faster queries
        db.run(`CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_data(timestamp)`, (err) => {
            if (err) {
                console.error('Error creating index:', err.message);
            } else {
                console.log('Index created successfully');
            }
        });
    }
});

// AWS IoT Core Configuration (commented out for now)
/*
const config = {
    endpoint: 'a1jdknvzevt8bn-ats.iot.us-east-1.amazonaws.com',
    certPath: '/home/pi/smart-garden-backend/awsIoT/certificate.pem.crt',
    keyPath: '/home/pi/smart-garden-backend/awsIoT/private.pem.key',
    caPath: '/home/pi/smart-garden-backend/awsIoT/root-ca.pem',
    clientId: 'ExpressServerClient'
};

// AWS IoT Core MQTT Configuration
const config_builder = iot.AwsIotMqttConnectionConfigBuilder.new_mtls_builder_from_path(
    config.certPath,
    config.keyPath
);
config_builder.with_certificate_authority_from_path(undefined, config.caPath);
config_builder.with_clean_session(false);
config_builder.with_client_id(config.clientId);
config_builder.with_endpoint(config.endpoint);
config_builder.with_port(8883);
config_builder.with_keep_alive_seconds(30);
config_builder.with_ping_timeout_ms(3000);
config_builder.with_protocol_operation_timeout_ms(60000);

const mqttConfig = config_builder.build();
const client = new mqtt.MqttClient(new io.ClientBootstrap());
const connection = client.new_connection(mqttConfig);
*/

// Air Quality Thresholds
const thresholds = {
    temperature: { low: 18, high: 28 }, // °C
    humidity: { low: 30, high: 70 },    // %
    gas: { low: 0, high: 500000 },      // ohms (lower means worse air quality)
    pressure: { low: 980, high: 1020 }  // hPa
};

// Air Quality Index (AQI) calculation
const calculateAQI = (gas, temperature, humidity) => {
    // Convert gas resistance to ppb (parts per billion) - this is an approximation
    // Lower resistance means higher gas concentration
    const gasConcentration = (1000000 / gas) * 100;

    // Base AQI on gas concentration with temperature and humidity adjustments
    let aqi = gasConcentration;

    // Adjust for temperature (optimal range 20-25°C)
    const tempFactor = Math.abs(temperature - 22.5) / 10;
    aqi *= (1 + tempFactor);

    // Adjust for humidity (optimal range 40-60%)
    const humidityFactor = Math.abs(humidity - 50) / 50;
    aqi *= (1 + humidityFactor);

    // Map to standard AQI range (0-500)
    aqi = Math.min(Math.max(aqi * 5, 0), 500);

    // AQI Categories:
    // 0-50: Good
    // 51-100: Moderate
    // 101-150: Unhealthy for Sensitive Groups
    // 151-200: Unhealthy
    // 201-300: Very Unhealthy
    // 301-500: Hazardous

    return Math.round(aqi);
};

// Simulate AWS IoT Core connection (dummy function)
const simulateAWSIoTConnection = () => {
    console.log('Simulating AWS IoT Core connection...');

    // Simulate receiving sensor data every 30 seconds
    setInterval(() => {
        const mockData = {
            temperature: 20 + Math.random() * 10, // 20-30°C
            humidity: 40 + Math.random() * 30,    // 40-70%
            gas: 200000 + Math.random() * 100000, // 200k-300k ohms
            pressure: 1000 + Math.random() * 20,  // 1000-1020 hPa
            timestamp: Math.floor(Date.now() / 1000)
        };

        console.log('Simulated sensor data received:', mockData);
        processSensorData(mockData);
    }, 30000); // Every 30 seconds

    console.log('AWS IoT Core simulation started - generating mock data every 30 seconds');
};

// Process sensor data (extracted from the original AWS IoT handler)
const processSensorData = (data) => {
    try {
        console.log('Processing sensor data:', data);

        const sensorEntry = {
            ...data,
            timestamp: new Date(data.timestamp * 1000),
        };
        sensorData.push(sensorEntry);

        // Generate Notifications
        const notifications = [];

        // Air Quality Notifications
        if (data.gas < thresholds.gas.low) {
            notifications.push({
                type: 'Poor Air Quality',
                message: 'High gas levels detected! Consider ventilating the area.',
                severity: 'danger'
            });
        }

        // Temperature Notifications
        if (data.temperature > thresholds.temperature.high) {
            notifications.push({
                type: 'High Temperature',
                message: `Temperature is above comfortable levels (${data.temperature.toFixed(1)}°C).`,
                severity: 'warning'
            });
        } else if (data.temperature < thresholds.temperature.low) {
            notifications.push({
                type: 'Low Temperature',
                message: `Temperature is below comfortable levels (${data.temperature.toFixed(1)}°C).`,
                severity: 'warning'
            });
        }

        // Humidity Notifications
        if (data.humidity > thresholds.humidity.high) {
            notifications.push({
                type: 'High Humidity',
                message: `Humidity is high (${data.humidity.toFixed(1)}%). This may affect air quality.`,
                severity: 'warning'
            });
        } else if (data.humidity < thresholds.humidity.low) {
            notifications.push({
                type: 'Low Humidity',
                message: `Humidity is low (${data.humidity.toFixed(1)}%). Consider using a humidifier.`,
                severity: 'warning'
            });
        }

        // Pressure Notifications
        if (data.pressure > thresholds.pressure.high) {
            notifications.push({
                type: 'High Pressure',
                message: `Pressure is high (${data.pressure.toFixed(1)} hPa).`,
                severity: 'info'
            });
        } else if (data.pressure < thresholds.pressure.low) {
            notifications.push({
                type: 'Low Pressure',
                message: `Pressure is low (${data.pressure.toFixed(1)} hPa).`,
                severity: 'info'
            });
        }

        if (notifications.length > 0) {
            scheduledNotifications.push(...notifications);
        }

        // Store in local database
        const query = `
            INSERT INTO sensor_data (temperature, humidity, gas, pressure, timestamp)
            VALUES (?, ?, ?, ?, ?)
        `;
        db.run(
            query,
            [data.temperature, data.humidity, data.gas, data.pressure, sensorEntry.timestamp],
            function (err) {
                if (err) {
                    console.error('Error storing sensor data:', err);
                } else {
                    console.log('Sensor data stored successfully');
                }
            }
        );
    } catch (error) {
        console.error('Error processing sensor data:', error);
    }
};

// Start AWS IoT simulation instead of real connection
// simulateAWSIoTConnection(); // Disabled to use real sensor data

// Routes
app.post('/api/sensors', (req, res) => {
    const { temperature, humidity, pressure, gas, reducing, nh3 } = req.body;
    const timestamp = new Date();

    const aqi = calculateAQI(gas, temperature, humidity);
    const sensorEntry = { temperature, humidity, pressure, gas, reducing, nh3, aqi, timestamp };
    sensorData.push(sensorEntry);

    // Insert into local database
    const query = `INSERT INTO sensor_data (temperature, humidity, pressure, gas, reducing, nh3, aqi, timestamp) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
    const values = [temperature, humidity, pressure, gas, reducing, nh3, aqi, timestamp];

    db.run(query, values, function (err) {
        if (err) {
            console.error('Error inserting data:', err);
            return res.status(500).send({ message: 'Database insertion failed' });
        }

        // Generate Notifications
        const notifications = [];

        // Air Quality Notifications
        if (gas < thresholds.gas.low) {
            notifications.push({
                type: 'Poor Air Quality',
                message: 'High gas levels detected! Consider ventilating the area.',
                severity: 'danger'
            });
        }

        // Temperature Notifications
        if (temperature > thresholds.temperature.high) {
            notifications.push({
                type: 'High Temperature',
                message: `Temperature is above comfortable levels (${temperature.toFixed(1)}°C).`,
                severity: 'warning'
            });
        } else if (temperature < thresholds.temperature.low) {
            notifications.push({
                type: 'Low Temperature',
                message: `Temperature is below comfortable levels (${temperature.toFixed(1)}°C).`,
                severity: 'warning'
            });
        }

        // Humidity Notifications
        if (humidity > thresholds.humidity.high) {
            notifications.push({
                type: 'High Humidity',
                message: `Humidity is high (${humidity.toFixed(1)}%). This may affect air quality.`,
                severity: 'warning'
            });
        } else if (humidity < thresholds.humidity.low) {
            notifications.push({
                type: 'Low Humidity',
                message: `Humidity is low (${humidity.toFixed(1)}%). Consider using a humidifier.`,
                severity: 'warning'
            });
        }

        console.log('Generated Notifications:', notifications);

        res.status(201).send({
            message: 'Data stored in database',
            notifications,
        });
    });
});

app.get('/api/notifications', (req, res) => {
    const notifications = [];

    if (sensorData.length > 0) {
        const latestData = sensorData[sensorData.length - 1];

        // Air Quality Notifications
        if (latestData.gas < thresholds.gas.low) {
            notifications.push({
                type: 'Poor Air Quality',
                message: 'High gas levels detected! Consider ventilating the area.',
                severity: 'danger'
            });
        }

        // Temperature Notifications
        if (latestData.temperature > thresholds.temperature.high) {
            notifications.push({
                type: 'High Temperature',
                message: `Temperature is above comfortable levels (${latestData.temperature.toFixed(1)}°C).`,
                severity: 'warning'
            });
        } else if (latestData.temperature < thresholds.temperature.low) {
            notifications.push({
                type: 'Low Temperature',
                message: `Temperature is below comfortable levels (${latestData.temperature.toFixed(1)}°C).`,
                severity: 'warning'
            });
        }

        // Humidity Notifications
        if (latestData.humidity > thresholds.humidity.high) {
            notifications.push({
                type: 'High Humidity',
                message: `Humidity is high (${latestData.humidity.toFixed(1)}%). This may affect air quality.`,
                severity: 'warning'
            });
        } else if (latestData.humidity < thresholds.humidity.low) {
            notifications.push({
                type: 'Low Humidity',
                message: `Humidity is low (${latestData.humidity.toFixed(1)}%). Consider using a humidifier.`,
                severity: 'warning'
            });
        }
    }

    res.json(notifications);
});

app.get('/api/sensors', (req, res) => {
    // Fetch data from database instead of in-memory array
    const query = `SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100`;
    db.all(query, [], (err, rows) => {
        if (err) {
            console.error('Error fetching sensor data:', err);
            return res.status(500).json({ error: 'Database error' });
        }

        // Convert database rows to the expected format
        const formattedData = rows.map(row => ({
            temperature: row.temperature,
            humidity: row.humidity,
            pressure: row.pressure,
            gas: row.gas,
            reducing: row.reducing,
            nh3: row.nh3,
            aqi: row.aqi,
            timestamp: row.timestamp
        }));

        res.json(formattedData);
    });
});

// LED Status page
app.get('/led-status', (req, res) => {
    res.sendFile(__dirname + '/led_status.html');
});

// Display Control page
app.get('/display-control', (req, res) => {
    res.sendFile(__dirname + '/display_control.html');
});

// Presentation page
app.get('/presentation', (req, res) => {
    res.sendFile(__dirname + '/presentation.html');
});

// Real Sensors Only page
app.get('/real-sensors', (req, res) => {
    res.sendFile(__dirname + '/real_sensors_presentation.html');
});

// School Presentation page
app.get('/school', (req, res) => {
    res.sendFile(__dirname + '/school_presentation.html');
});

// LED Control API
app.post('/api/led/control', (req, res) => {
    const { action } = req.body;

    if (action === 'start') {
        // Start LED control script
        const { spawn } = require('child_process');
        const ledProcess = spawn('python3', [__dirname + '/enviro_led_gpio.py']);

        ledProcess.stdout.on('data', (data) => {
            console.log(`LED Control: ${data}`);
        });

        ledProcess.stderr.on('data', (data) => {
            console.error(`LED Control Error: ${data}`);
        });

        res.json({ message: 'LED control started', pid: ledProcess.pid });
    } else if (action === 'stop') {
        // Stop LED control script
        const { exec } = require('child_process');
        exec('pkill -f enviro_led_gpio.py', (error, stdout, stderr) => {
            if (error) {
                console.error(`Error stopping LED control: ${error}`);
                return res.status(500).json({ error: 'Failed to stop LED control' });
            }
            res.json({ message: 'LED control stopped' });
        });
    } else {
        res.status(400).json({ error: 'Invalid action. Use "start" or "stop"' });
    }
});

// LCD Control API
app.post('/api/lcd/control', (req, res) => {
    const { action } = req.body;

    if (action === 'start') {
        // Start LCD display script
        const { spawn } = require('child_process');
        const lcdProcess = spawn('python3', [__dirname + '/simple_lcd_display.py']);

        lcdProcess.stdout.on('data', (data) => {
            console.log(`LCD Display: ${data}`);
        });

        lcdProcess.stderr.on('data', (data) => {
            console.error(`LCD Display Error: ${data}`);
        });

        res.json({ message: 'LCD display started', pid: lcdProcess.pid });
    } else if (action === 'stop') {
        // Stop LCD display script
        const { exec } = require('child_process');
        exec('pkill -f simple_lcd_display.py', (error, stdout, stderr) => {
            if (error) {
                console.error(`Error stopping LCD display: ${error}`);
                return res.status(500).json({ error: 'Failed to stop LCD display' });
            }
            res.json({ message: 'LCD display stopped' });
        });
    } else {
        res.status(400).json({ error: 'Invalid action. Use "start" or "stop"' });
    }
});

// All Sensors Control API
app.post('/api/sensors/control', (req, res) => {
    const { action } = req.body;

    if (action === 'start') {
        // Start all sensors script
        const { spawn } = require('child_process');
        const sensorsProcess = spawn('python3', [__dirname + '/enviro_all_sensors.py']);

        sensorsProcess.stdout.on('data', (data) => {
            console.log(`All Sensors: ${data}`);
        });

        sensorsProcess.stderr.on('data', (data) => {
            console.error(`All Sensors Error: ${data}`);
        });

        res.json({ message: 'All sensors started', pid: sensorsProcess.pid });
    } else if (action === 'stop') {
        // Stop all sensors script
        const { exec } = require('child_process');
        exec('pkill -f enviro_all_sensors.py', (error, stdout, stderr) => {
            if (error) {
                console.error(`Error stopping all sensors: ${error}`);
                return res.status(500).json({ error: 'Failed to stop all sensors' });
            }
            res.json({ message: 'All sensors stopped' });
        });
    } else {
        res.status(400).json({ error: 'Invalid action. Use "start" or "stop"' });
    }
});

// School Smart Alerts Control API
app.post('/api/school/control', (req, res) => {
    const { action } = req.body;

    if (action === 'start') {
        // Start school smart alerts script
        const { spawn } = require('child_process');
        const schoolProcess = spawn('python3', [__dirname + '/school_smart_alerts.py']);

        schoolProcess.stdout.on('data', (data) => {
            console.log(`School Alerts: ${data}`);
        });

        schoolProcess.stderr.on('data', (data) => {
            console.error(`School Alerts Error: ${data}`);
        });

        res.json({ message: 'School smart alerts started', pid: schoolProcess.pid });
    } else if (action === 'stop') {
        // Stop school smart alerts script
        const { exec } = require('child_process');
        exec('pkill -f school_smart_alerts.py', (error, stdout, stderr) => {
            if (error) {
                console.error(`Error stopping school alerts: ${error}`);
                return res.status(500).json({ error: 'Failed to stop school alerts' });
            }
            res.json({ message: 'School smart alerts stopped' });
        });
    } else {
        res.status(400).json({ error: 'Invalid action. Use "start" or "stop"' });
    }
});

// Cron Jobs for Air Quality Checks
cron.schedule('*/30 * * * *', () => { // Runs every 30 minutes
    const notification = {
        type: 'Air Quality Check',
        message: 'Time to check air quality readings and ensure proper ventilation.',
        severity: 'info',
        timestamp: new Date(),
    };
    scheduledNotifications.push(notification);
    console.log('Scheduler: New Air Quality Check Added:', notification);
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

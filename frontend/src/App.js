import React, { useEffect, useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Tooltip as BootstrapTooltip } from 'react-bootstrap';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function App() {
    const [sensorData, setSensorData] = useState([]);
    const [notifications, setNotifications] = useState([]);
    const [showNotifications, setShowNotifications] = useState(false);
    const [activeTab, setActiveTab] = useState("Dashboard");
    const [weather, setWeather] = useState(null);
    const [showAlertDropdown, setShowAlertDropdown] = useState(false);

    const thresholds = {
        temperature: { low: 18, high: 28 }, // °C
        humidity: { low: 30, high: 70 },    // %
        gas: { low: 0, high: 500000 },      // ohms (lower means worse air quality)
        pressure: { low: 980, high: 1020 }  // hPa
    };

    // Fetch sensor data and weather data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://localhost:3000/api/sensors');
                const data = await response.json();
                setSensorData(data);
                generateNotifications(data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        const fetchWeather = async () => {
            try {
                const apiKey = 'a4ad2ad2ef48415f75761fe3bfa19661';
                const response = await fetch(
                    `https://api.openweathermap.org/data/2.5/forecast?q=Tel-Aviv&units=metric&appid=${apiKey}`
                );
                const data = await response.json();
                setWeather(data);
            } catch (error) {
                console.error('Error fetching weather data:', error);
            }
        };

        fetchData();
        fetchWeather();

        const interval = setInterval(() => {
            fetchData();
            fetchWeather();
        }, 300000); // Fetch every 5 minutes

        return () => clearInterval(interval);
    }, []);

    const generateNotifications = (data) => {
        if (!data || !data.length) return;

        const latestData = data[data.length - 1];
        const newNotifications = [];

        // Air Quality Notifications
        if (latestData.gas && latestData.gas < thresholds.gas.low) {
            newNotifications.push({
                type: 'Poor Air Quality',
                message: `High gas levels detected! Consider ventilating the area.`,
                severity: 'danger'
            });
        }

        // Temperature Notifications
        if (latestData.temperature && latestData.temperature > thresholds.temperature.high) {
            newNotifications.push({
                type: 'High Temperature',
                message: `Temperature is above comfortable levels (${latestData.temperature.toFixed(1)}°C).`,
                severity: 'warning'
            });
        } else if (latestData.temperature && latestData.temperature < thresholds.temperature.low) {
            newNotifications.push({
                type: 'Low Temperature',
                message: `Temperature is below comfortable levels (${latestData.temperature.toFixed(1)}°C).`,
                severity: 'warning'
            });
        }

        // Humidity Notifications
        if (latestData.humidity && latestData.humidity > thresholds.humidity.high) {
            newNotifications.push({
                type: 'High Humidity',
                message: `Humidity is high (${latestData.humidity.toFixed(1)}%). This may affect air quality.`,
                severity: 'warning'
            });
        } else if (latestData.humidity && latestData.humidity < thresholds.humidity.low) {
            newNotifications.push({
                type: 'Low Humidity',
                message: `Humidity is low (${latestData.humidity.toFixed(1)}%). Consider using a humidifier.`,
                severity: 'warning'
            });
        }

        setNotifications(newNotifications);
    };

    const createChartData = (key) => {
        return {
            labels: sensorData.map(entry => new Date(entry.timestamp).toLocaleTimeString()),
            datasets: [
                {
                    label: key.charAt(0).toUpperCase() + key.slice(1),
                    data: sensorData.map(entry => entry[key]),
                    borderColor:
                        key === 'temperature' ? '#ff6b6b' :
                            key === 'humidity' ? '#4dabf7' :
                                key === 'gas' ? '#69db7c' :
                                    key === 'pressure' ? '#ffd43b' :
                                        '#748ffc',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    tension: 0.4,
                    fill: true,
                },
            ],
        };
    };

    const getAirQualityStatus = () => {
        if (!sensorData || !sensorData.length) return { text: 'No Data', color: 'secondary' };

        const latestData = sensorData[sensorData.length - 1];

        if (latestData.gas && latestData.gas < thresholds.gas.low) {
            return { text: 'Poor', color: 'danger' };
        } else if (latestData.gas && latestData.gas < thresholds.gas.low * 2) {
            return { text: 'Fair', color: 'warning' };
        } else {
            return { text: 'Good', color: 'success' };
        }
    };

    const airQualityStatus = getAirQualityStatus();

    const getAQIColor = (aqi) => {
        if (aqi <= 50) return '#00e400';      // Good - Green
        if (aqi <= 100) return '#ffff00';     // Moderate - Yellow
        if (aqi <= 150) return '#ff7e00';     // Unhealthy for Sensitive Groups - Orange
        if (aqi <= 200) return '#ff0000';     // Unhealthy - Red
        if (aqi <= 300) return '#8f3f97';     // Very Unhealthy - Purple
        return '#7e0023';                     // Hazardous - Maroon
    };

    const getAQIMessage = (aqi) => {
        if (aqi <= 50) return 'Air quality is good. Perfect for outdoor activities!';
        if (aqi <= 100) return 'Air quality is moderate. Sensitive individuals should reduce prolonged outdoor exposure.';
        if (aqi <= 150) return 'Unhealthy for sensitive groups. Reduce outdoor activities.';
        if (aqi <= 200) return 'Unhealthy air quality. Avoid prolonged outdoor exposure.';
        if (aqi <= 300) return 'Very unhealthy air quality. Avoid outdoor activities.';
        return 'Hazardous air quality. Stay indoors!';
    };

    // Add this new function for example alerts
    const generateExampleAlerts = () => {
        const exampleAlerts = [
            {
                type: 'Temperature Alert',
                message: 'Temperature is too high (32°C). Consider cooling the area.',
                severity: 'danger'
            },
            {
                type: 'Humidity Alert',
                message: 'Humidity is below optimal range (25%). Consider using a humidifier.',
                severity: 'warning'
            },
            {
                type: 'Air Quality Alert',
                message: 'Poor air quality detected. Please ventilate the area.',
                severity: 'danger'
            },
            {
                type: 'Pressure Alert',
                message: 'Unusual pressure change detected (965 hPa).',
                severity: 'warning'
            },
            {
                type: 'System Status',
                message: 'All sensors are functioning normally.',
                severity: 'success'
            }
        ];
        setNotifications(exampleAlerts);
    };

    // Add this useEffect to generate example alerts
    useEffect(() => {
        generateExampleAlerts();
    }, []);

    return (
        <div className="container my-5">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1 className="text-center mb-0">🌬️ Air Quality Monitor</h1>
                <div className="notification-bell" onClick={() => setShowAlertDropdown(!showAlertDropdown)}>
                    🔔
                    {notifications.length > 0 && (
                        <span className="notification-badge">{notifications.length}</span>
                    )}
                    {showAlertDropdown && (
                        <div className="alert-dropdown">
                            <h6 className="dropdown-header">Active Alerts</h6>
                            {notifications.length === 0 ? (
                                <div className="dropdown-item">No active alerts</div>
                            ) : (
                                notifications.map((note, index) => (
                                    <div key={index} className={`dropdown-item alert-${note.severity}`}>
                                        <strong>{note.type}:</strong> {note.message}
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Current Status Card */}
            <div className="card mb-4 shadow-sm">
                <div className="card-body">
                    <h3 className="card-title text-center">Current Air Quality</h3>
                    <div className="text-center">
                        <h2 className={`display-4 text-${airQualityStatus.color}`}>
                            {airQualityStatus.text}
                        </h2>
                    </div>
                    {sensorData && sensorData.length > 0 && (
                        <div className="row text-center mt-3">
                            <div className="col-md-3">
                                <h5>Temperature</h5>
                                <p className="h3">{sensorData[sensorData.length - 1].temperature ? sensorData[sensorData.length - 1].temperature.toFixed(1) : 'N/A'}°C</p>
                            </div>
                            <div className="col-md-3">
                                <h5>Humidity</h5>
                                <p className="h3">{sensorData[sensorData.length - 1].humidity ? sensorData[sensorData.length - 1].humidity.toFixed(1) : 'N/A'}%</p>
                            </div>
                            <div className="col-md-3">
                                <h5>Pressure</h5>
                                <p className="h3">{sensorData[sensorData.length - 1].pressure ? sensorData[sensorData.length - 1].pressure.toFixed(1) : 'N/A'} hPa</p>
                            </div>
                            <div className="col-md-3">
                                <h5>Gas</h5>
                                <p className="h3">{sensorData[sensorData.length - 1].gas ? (sensorData[sensorData.length - 1].gas / 1000).toFixed(1) : 'N/A'}k Ω</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Weather Section */}
            {weather && weather.city && (
                <div className="weather-alert mb-4 p-3 rounded shadow-sm bg-info text-white">
                    <h4>🌤️ Weather Forecast</h4>
                    <p>
                        <strong>Location:</strong> {weather.city.name}
                    </p>
                    <p>
                        <strong>Next 3 Hours:</strong>{' '}
                        {weather.list[0].weather[0].description}, {weather.list[0].main.temp}°C
                    </p>
                </div>
            )}

            {/* Notifications Section */}
            <div className="mb-4">
                <button
                    className="btn btn-outline-primary"
                    onClick={() => setShowNotifications(!showNotifications)}
                >
                    {showNotifications ? "Hide Alerts" : "Show Alerts"}
                </button>

                {showNotifications && (
                    <div className="notifications mt-3 p-3 rounded shadow-sm">
                        <h4>Alerts</h4>
                        {notifications.length === 0 && (
                            <p className="text-muted">No alerts at the moment.</p>
                        )}
                        <ul className="list-group">
                            {notifications.map((note, index) => (
                                <li key={index} className={`list-group-item list-group-item-${note.severity}`}>
                                    <strong>{note.type}:</strong> {note.message}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Navigation Tabs */}
            <ul className="nav nav-tabs justify-content-center mb-4">
                {["Dashboard", "Graphs"].map(tab => (
                    <li key={tab} className="nav-item">
                        <button
                            className={`nav-link ${activeTab === tab ? "active" : ""}`}
                            onClick={() => setActiveTab(tab)}
                        >
                            {tab}
                        </button>
                    </li>
                ))}
            </ul>

            {/* Dashboard and Graph Views */}
            {activeTab === "Graphs" && (
                <div className="graphs-container">
                    <div className="row">
                        <div className="col-md-6 mb-4">
                            <div className="card">
                                <div className="card-body">
                                    <h5 className="card-title">Temperature & Humidity</h5>
                                    <Line data={createChartData('temperature')} />
                                    <Line data={createChartData('humidity')} />
                                </div>
                            </div>
                        </div>
                        <div className="col-md-6 mb-4">
                            <div className="card">
                                <div className="card-title">
                                    <h5 className="card-title">Air Quality & Pressure</h5>
                                    <Line data={createChartData('gas')} />
                                    <Line data={createChartData('pressure')} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div className="sensor-grid">
                <div className="sensor-card aqi-card"
                    style={{ borderColor: getAQIColor(sensorData && sensorData.length > 0 ? sensorData[sensorData.length - 1].aqi : 0) }}
                    title="Air Quality Index (AQI) measures how clean or polluted the air is. Higher values indicate worse air quality.">
                    <h2>Air Quality Index</h2>
                    <div className="aqi-value" style={{ color: getAQIColor(sensorData && sensorData.length > 0 ? sensorData[sensorData.length - 1].aqi : 0) }}>
                        {sensorData && sensorData.length > 0 && sensorData[sensorData.length - 1].aqi ? sensorData[sensorData.length - 1].aqi : 'N/A'}
                    </div>
                    <p className="aqi-message">{getAQIMessage(sensorData && sensorData.length > 0 ? sensorData[sensorData.length - 1].aqi : 0)}</p>
                </div>

                <div className="sensor-card"
                    title="Temperature in Celsius. Ideal range: 18-28°C">
                    <h2>Temperature</h2>
                    <p>{sensorData && sensorData.length > 0 && sensorData[sensorData.length - 1].temperature ? sensorData[sensorData.length - 1].temperature.toFixed(1) : 'N/A'}°C</p>
                </div>

                <div className="sensor-card"
                    title="Relative humidity percentage. Ideal range: 30-70%">
                    <h2>Humidity</h2>
                    <p>{sensorData && sensorData.length > 0 && sensorData[sensorData.length - 1].humidity ? sensorData[sensorData.length - 1].humidity.toFixed(1) : 'N/A'}%</p>
                </div>

                <div className="sensor-card"
                    title="Atmospheric pressure in hectopascals (hPa). Normal range: 980-1020 hPa">
                    <h2>Pressure</h2>
                    <p>{sensorData && sensorData.length > 0 && sensorData[sensorData.length - 1].pressure ? sensorData[sensorData.length - 1].pressure.toFixed(1) : 'N/A'} hPa</p>
                </div>
            </div>

            <style>{`
                .sensor-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    padding: 20px;
                }
                
                .sensor-card {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border: 2px solid #ddd;
                    text-align: center;
                    cursor: help;
                    transition: transform 0.2s ease-in-out;
                }
                
                .sensor-card:hover {
                    transform: translateY(-5px);
                }
                
                .aqi-card {
                    grid-column: 1 / -1;
                }
                
                .aqi-value {
                    font-size: 48px;
                    font-weight: bold;
                    margin: 20px 0;
                }
                
                .aqi-message {
                    font-size: 16px;
                    margin-top: 10px;
                }

                .notification-bell {
                    position: relative;
                    cursor: pointer;
                    font-size: 24px;
                    padding: 10px;
                }

                .notification-badge {
                    position: absolute;
                    top: 0;
                    right: 0;
                    background-color: red;
                    color: white;
                    border-radius: 50%;
                    padding: 2px 6px;
                    font-size: 12px;
                }

                .alert-dropdown {
                    position: absolute;
                    right: 0;
                    top: 100%;
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    min-width: 300px;
                    z-index: 1000;
                }

                .dropdown-header {
                    padding: 10px 15px;
                    border-bottom: 1px solid #ddd;
                    font-weight: bold;
                }

                .dropdown-item {
                    padding: 10px 15px;
                    border-bottom: 1px solid #eee;
                }

                .dropdown-item:last-child {
                    border-bottom: none;
                }

                .alert-danger {
                    color: #dc3545;
                }

                .alert-warning {
                    color: #ffc107;
                }

                .alert-success {
                    color: #28a745;
                }
            `}</style>

            <script>
                {`
                    // Initialize all tooltips
                    document.addEventListener('DOMContentLoaded', function() {
                        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
                        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                            return new bootstrap.Tooltip(tooltipTriggerEl)
                        });
                    });
                `}
            </script>
        </div>
    );
}

export default App;

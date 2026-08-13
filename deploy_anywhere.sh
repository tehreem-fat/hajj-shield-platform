#!/bin/bash
# HAJJ-SHIELD - Deploy Anywhere

echo "🏛️  HAJJ-SHIELD Deployment Script"
echo "=================================="

# Clone from GitHub
git clone https://github.com/tehreem-fat/hajj-shield-platform.git
cd hajj-shield-platform

# Create virtual environment
python3 -m venv hajj_env
source hajj_env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Generate data and models
python3 module_1_slice_security/generate_training_data.py
python3 module_1_slice_security/ddos_detector.py
python3 module_2_crowd_anomaly/sensor_simulator.py
python3 module_2_crowd_anomaly/anomaly_detector.py
python3 module_2_crowd_anomaly/heatmap_generator.py

echo "✅ Deployment complete!"
echo "📊 Start dashboard: python3 -m http.server 8000"
echo "🌐 Access: http://localhost:8000/dashboard/index.html"

#!/bin/bash
echo "🔧 Setting up HAJJ-SHIELD environment..."

# 1. Install required system packages
echo "📦 Installing system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv

# 2. Navigate to project
cd ~/hajj-shield/Hajj-Shield

# 3. Remove old venv if exists
rm -rf hajj_env

# 4. Create new virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv hajj_env

# 5. Activate it
source hajj_env/bin/activate

# 6. Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# 7. Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# 8. Verify installation
echo "✅ Verifying installation..."
python3 -c "
import pandas, numpy, sklearn, joblib, cryptography, folium
print('All packages imported successfully!')
print(f'pandas: {pandas.__version__}')
print(f'numpy: {numpy.__version__}')
print(f'scikit-learn: {sklearn.__version__}')
"

echo "✅ Setup complete!"
echo "📂 Project location: ~/hajj-shield/Hajj-Shield"
echo "🔧 Activate environment: source hajj_env/bin/activate"#!/bin/bash
echo "🔧 Setting up HAJJ-SHIELD environment..."

# 1. Install required system packages
echo "📦 Installing system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv

# 2. Navigate to project
cd ~/hajj-shield/Hajj-Shield

# 3. Remove old venv if exists
rm -rf hajj_env

# 4. Create new virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv hajj_env

# 5. Activate it
source hajj_env/bin/activate

# 6. Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# 7. Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# 8. Verify installation
echo "✅ Verifying installation..."
python3 -c "
import pandas, numpy, sklearn, joblib, cryptography, folium
print('All packages imported successfully!')
print(f'pandas: {pandas.__version__}')
print(f'numpy: {numpy.__version__}')
print(f'scikit-learn: {sklearn.__version__}')
"

echo "✅ Setup complete!"
echo "📂 Project location: ~/hajj-shield/Hajj-Shield"
echo "🔧 Activate environment: source hajj_env/bin/activate"

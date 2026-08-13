#!/bin/bash
echo "🔧 COMPLETE VIRTUAL ENVIRONMENT FIX"

cd ~/hajj-shield/Hajj-Shield

# 1. Deactivate any existing environment
deactivate 2>/dev/null || true

# 2. Remove old hajj_env
echo "📦 Removing old virtual environment..."
rm -rf hajj_env

# 3. Create new virtual environment
echo "🐍 Creating new virtual environment..."
python3 -m venv hajj_env

# 4. Activate it
echo "🔧 Activating virtual environment..."
source hajj_env/bin/activate

# 5. Verify activation
echo "✅ Python location: $(which python3)"

# 6. Upgrade pip
echo "⬆️  Upgrading pip..."
python3 -m pip install --upgrade pip

# 7. Install packages
echo "📦 Installing packages..."
python3 -m pip install numpy joblib pandas scikit-learn cryptography folium matplotlib

# 8. Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "export PYTHONPATH=\"\${PYTHONPATH}:/home/ubuntu/hajj-shield/Hajj-Shield\"" >> ~/.bashrc

# 9. Verify
echo "✅ Verifying installation..."
python3 -c "
import numpy, joblib, pandas, sklearn, cryptography, folium
print('✅ All packages imported successfully!')
print(f'numpy: {numpy.__version__}')
print(f'joblib: {joblib.__version__}')
print(f'pandas: {pandas.__version__}')
"

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the demo:"
echo "  cd ~/hajj-shield/Hajj-Shield"
echo "  source hajj_env/bin/activate"
echo "  python3 demo_scenario/hajj_day3_emergency.py"

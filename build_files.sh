python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
python3 -m pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Run Django collectstatic to gather static files
python3 manage.py collectstatic --noinput
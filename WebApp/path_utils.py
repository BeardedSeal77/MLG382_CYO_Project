import os

# Get the absolute path to the project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Get absolute path to a file in the data directory
def get_data_path(filename):
    return os.path.join(DATA_DIR, filename)

# Get absolute path to a file in the models directory
def get_model_path(filename):
    return os.path.join(MODELS_DIR, filename)
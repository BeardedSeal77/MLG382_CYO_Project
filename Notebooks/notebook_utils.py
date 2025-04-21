import sys
import os

# This script is designed to be run in a Jupyter Notebook environment.
# It adds the 'src' directory to sys.path, allowing the notebook to import modules from src easily.
def setup_src_path():
    
    # Get the current file's directory and the root directory of the project
    # This assumes the script is located in a 'Notebooks' directory at the same level as 'src'
    current_path = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.abspath(os.path.join(current_path, '..'))
    src_path = os.path.join(root_path, 'src')

    if src_path not in sys.path:
        sys.path.append(src_path)
        print(f"Added to sys.path: {src_path}")
    else:
        print("src path already exists in sys.path")

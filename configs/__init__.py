"""
Config module for diffusion3d
"""
import yaml
import os

# Load configuration from YAML file
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
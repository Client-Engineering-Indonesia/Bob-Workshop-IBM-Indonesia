"""
Utility functions for Trade Settlement Prediction
Helper functions used across the project
"""

import pandas as pd
import numpy as np


def load_config():
    """Load configuration settings"""
    config = {
        'data_path': 'Data/',
        'model_path': 'models/',
        'results_path': 'results/',
        'random_state': 42
    }
    return config


def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"


def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return (part / total) * 100

# Made with Bob

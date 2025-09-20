import streamlit as st
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the streamlit app
from app.streamlit_app import *

# This file serves as the entry point for Vercel to run the Streamlit dashboard
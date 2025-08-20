#!/usr/bin/env python3
"""
Vehicle Dashboard Setup and Launch Script
Run this script to set up and launch the vehicle registration dashboard
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_banner():
    """Print project banner"""
    banner = """
    🚗 Vehicle Registration Dashboard
    ================================
    Interactive Analytics for Vehicle Registration Data
    Built for Backend Developer Internship Assignment
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    directories = ["data", "data/raw", "data/processed"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")

def check_database():
    """Check if database exists and has data"""
    db_path = "data/vehicle_data.db"
    
    if not os.path.exists(db_path):
        print(f"⚠️ Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vehicle_registrations")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"✅ Database found with {count:,} records")
            return True
        else:
            print("⚠️ Database exists but is empty")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def generate_sample_data():
    """Generate sample data if database is empty"""
    print("\n📊 Generating sample vehicle registration data...")
    
    try:
        # Change to src directory to run data collector
        current_dir = os.getcwd()
        
        # Run data collector
        result = subprocess.run([
            sys.executable, "src/data_collector.py"
        ], capture_output=True, text=True, cwd=current_dir)
        
        if result.returncode == 0:
            print("✅ Sample data generated successfully")
            print(result.stdout)
            return True
        else:
            print(f"❌ Error generating data: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running data collector: {e}")
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("\n🚀 Launching dashboard...")
    print("Dashboard will open in your default browser")
    print("Press Ctrl+C to stop the dashboard")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def run_jupyter_analysis():
    """Launch Jupyter notebook for analysis"""
    print("\n📓 Would you like to run the analysis notebook? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice in ['y', 'yes']:
        try:
            subprocess.run([
                sys.executable, "-m", "jupyter", "notebook", 
                "notebooks/vehicle_analysis.ipynb"
            ])
        except Exception as e:
            print(f"❌ Error launching Jupyter: {e}")

def main():
    """Main setup and launch function"""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        return
    
    # Step 3: Setup directories
    setup_directories()
    
    # Step 4: Check/generate data
    if not check_database():
        print("\nGenerating sample data for demonstration...")
        if not generate_sample_data():
            print("❌ Failed to generate sample data")
            return
    
    # Step 5: Show options
    print("\n🎯 Setup completed successfully!")
    print("\nAvailable options:")
    print("1. Launch Streamlit Dashboard")
    print("2. Run Jupyter Analysis Notebook")
    print("3. Both")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            launch_dashboard()
            break
        elif choice == "2":
            run_jupyter_analysis()
            break
        elif choice == "3":
            print("\nLaunching Jupyter notebook first...")
            run_jupyter_analysis()
            print("\nNow launching dashboard...")
            launch_dashboard()
            break
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    main()

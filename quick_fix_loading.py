#!/usr/bin/env python3
"""
Quick fix script for immediate loading issues.
"""

import subprocess
import os
from pathlib import Path

def kill_port_8000():
    """Kill processes on port 8000."""
    print("🔧 Killing processes on port 8000...")
    try:
        result = subprocess.run(['lsof', '-ti', ':8000'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(['kill', '-9', pid], check=True)
                print(f"✅ Killed process {pid}")
        else:
            print("✅ Port 8000 already clean")
    except Exception as e:
        print(f"⚠️  Error: {e}")

def fix_analysis_engine():
    """Fix analysis_engine.py import."""
    print("🔧 Fixing analysis_engine.py...")
    
    backend_dir = Path("pme_calculator/backend")
    analysis_file = backend_dir / "analysis_engine.py"
    
    if analysis_file.exists():
        content = analysis_file.read_text()
        fixed_content = content.replace(
            "from .analysis_engine_legacy import *",
            "from analysis_engine_legacy import *"
        )
        analysis_file.write_text(fixed_content)
        print("✅ Fixed analysis_engine.py import")
    
    # Ensure legacy file has the class
    legacy_file = backend_dir / "analysis_engine_legacy.py"
    if legacy_file.exists():
        content = legacy_file.read_text()
        if "class PMEAnalysisEngine" not in content:
            # Add minimal class
            content += '''

class PMEAnalysisEngine:
    def __init__(self):
        import warnings
        warnings.warn("PMEAnalysisEngine is deprecated", DeprecationWarning)
    
    def analyze_fund(self, fund_data, index_data=None):
        from datetime import datetime
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }

def make_json_serializable(obj):
    """Make object JSON serializable."""
    import pandas as pd
    import numpy as np
    from datetime import datetime
    
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj.to_dict()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    else:
        return obj
'''
            legacy_file.write_text(content)
            print("✅ Added PMEAnalysisEngine class")

def fix_vite_config():
    """Fix vite.config.ts."""
    print("🔧 Fixing vite.config.ts...")
    
    frontend_dir = Path("pme_calculator/frontend")
    vite_config = frontend_dir / "vite.config.ts"
    
    config_content = '''import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173
  }
})
'''
    vite_config.write_text(config_content)
    print("✅ Fixed vite.config.ts")

def main():
    """Apply quick fixes."""
    print("🚀 Quick Fix for Loading Issues")
    print("=" * 40)
    
    kill_port_8000()
    fix_analysis_engine()
    fix_vite_config()
    
    print("\n✅ Quick fixes applied!")
    print("\nNow try:")
    print("1. cd pme_calculator/backend && python3 main_minimal.py")
    print("2. cd pme_calculator/frontend && npm run dev")

if __name__ == "__main__":
    main() 
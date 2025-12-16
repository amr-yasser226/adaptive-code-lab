#!/usr/bin/env python
"""
ACCL Application Runner
Initializes database and starts the Flask development server
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

def main():
    """Main entry point"""
    print("=" * 60)
    print("ACCL - Adaptive Collaborative Code Lab")
    print("=" * 60)
    print()
    
    # Check if app.py exists
    app_path = project_root / 'src' / 'web' / 'app.py'
    if not app_path.exists():
        print(f"ERROR: app.py not found at {app_path}")
        sys.exit(1)
    
    print("[OK] Found Flask application")
    print(f"  Location: {app_path}")
    print()
    
    # Check templates
    templates_path = project_root / 'src' / 'web' / 'templates'
    if templates_path.exists():
        template_files = list(templates_path.glob('*.html')) + list(templates_path.glob('auth/*.html'))
        print(f"[OK] Found {len(template_files)} template files")
    print()
    
    # Check static files
    static_path = project_root / 'src' / 'web' / 'static'
    if static_path.exists():
        css_files = list((static_path / 'css').glob('*.css'))
        js_files = list((static_path / 'js').glob('*.js'))
        print(f"[OK] Found {len(css_files)} CSS and {len(js_files)} JS files")
    print()
    
    # Check database
    db_path = project_root / 'data' / 'Accl_DB.db'
    if db_path.exists():
        print(f"[OK] Database found: {db_path}")
    else:
        print(f"[WARN] Database not found at {db_path}")
        print("  Run: python src/infrastructure/database/create_db.py")
    print()
    
    print("=" * 60)
    print("Starting ACCL Flask Application...")
    print("=" * 60)
    print()
    print("Development server will start at: http://localhost:5000")
    print()
    print("Demo Credentials:")
    print("  Student:    student@example.com / password123")
    print("  Instructor: instructor@example.com / password123")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Change to web directory and run Flask
    web_dir = project_root / 'src' / 'web'
    os.chdir(web_dir)
    sys.path.insert(0, str(web_dir))
    
    try:
        # Import and run app using factory pattern
        import app as app_module
        
        # Create the Flask app using factory
        app = app_module.create_app()
        
        # Run development server
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    
    except ImportError as e:
        print(f"ERROR: Failed to import Flask app: {e}")
        print("\nMake sure dependencies are installed:")
        print("  pip install -r requirements.txt")
        print(f"\nError details: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()


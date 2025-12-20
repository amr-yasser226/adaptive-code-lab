import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def kill_port_process(port):
    """Attempt to kill any process using the specified port."""
    import platform
    import subprocess
    import signal
    
    system = platform.system().lower()
    print(f"Checking for existing processes on port {port}...")
    
    try:
        if "windows" in system:
            # Find PID using port
            cmd = f"netstat -ano | findstr :^{port}" # Standard port check
            # For robustness, we check specifically for LISTENING
            output = subprocess.check_output(f"netstat -ano | findstr LISTENING | findstr :{port}", shell=True, text=True)
            for line in output.strip().split('\n'):
                if str(port) in line:
                    pid = line.strip().split()[-1]
                    if pid and pid != "0":
                        print(f"  → Found process {pid} on Windows. Terminating...")
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        else:
            # Linux/macOS
            try:
                # Use fuser if available
                subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)
                print(f"  → Port {port} cleared using fuser.")
            except:
                # Fallback to lsof
                output = subprocess.check_output(["lsof", "-t", f"-i:{port}"], text=True)
                for pid in output.strip().split('\n'):
                    if pid:
                        print(f"  → Found process {pid} on Linux. Terminating...")
                        os.kill(int(pid), signal.SIGKILL)
    except Exception:
        # If port is free or command fails, just continue
        pass

def main():
    # Navigate to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("==========================================")
    print("STARTING ACCL PRODUCTION SERVER")
    print("==========================================")

    # 0. Clear port 5000 if in use
    kill_port_process(5000)

    # Check if .env exists
    env_path = project_root / '.env'
    if not env_path.exists():
        print("❌ ERROR: .env file not found! Please create it from .env.example")
        sys.exit(1)

    load_dotenv(env_path)

    # Detect Platform
    is_windows = sys.platform.startswith('win')

    if is_windows:
        print("Detected Windows environment. Using Waitress...")
        try:
            import waitress
        except ImportError:
            print("❌ ERROR: Waitress not found. Run 'pip install waitress'")
            sys.exit(1)
        
        from wsgi import app
        print("🚀 Server starting at http://localhost:5000")
        print("Press CTRL+C to stop the server")
        waitress.serve(app, host='0.0.0.0', port=5000)
    else:
        print("Detected Unix-like environment. Using Gunicorn...")
        # We try to use the gunicorn executable in the same bin as python
        gunicorn_path = Path(sys.executable).parent / 'gunicorn'
        if not gunicorn_path.exists():
            gunicorn_path = 'gunicorn' # Fallback to system path

        cmd = [
            str(gunicorn_path),
            "--workers", "4",
            "--bind", "0.0.0.0:5000",
            "wsgi:app"
        ]
        
        print("🚀 Server starting at http://localhost:5000")
        print("Press CTRL+C to stop the server")
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\nStopping server...")
        except Exception as e:
            print(f"❌ Error starting Gunicorn: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()

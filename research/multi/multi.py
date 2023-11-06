#! python3.10

"""

This control different python processes with separate virtual envs.

being sufficiently ISO with K8 or compose interface allows the user to use those
solutions instead of the multi.py. (which should provide a much robust
scaling options than this.)

Thefor it is self-prohibited to implement any buisness logic in this and is
prefered to use the orchestrator to this intent (which is spawnable alone trough
a blade)

"""


import sys
import json
import argparse
import yaml
from multiprocessing import Process
import time
import os
import subprocess
from venv import EnvBuilder


def ensure_virtualenv(venv_path):
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}")
        builder = EnvBuilder(with_pip=True)
        builder.create(venv_path)
        
        # After creating the venv, ensure that core dependencies are installed 
        pip_path = os.path.join(venv_path, 'bin', 'pip')
        requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        if os.path.exists(requirements_path):
            subprocess.call([pip_path, 'install', '-r', requirements_path])
        else:
            print(f"WARNING: requirements.txt not found at {requirements_path} - proceeding without installing packages.")
    else:
        print(f"Virtual environment already exists at {venv_path}")

def run_blade_server(module_config, topology):
    blade_path = "blades/blade.py"
    if not os.path.exists(blade_path):
        print(f"ERROR: '{blade_path}' does not exist in the current directory.", file=sys.stderr)
        return

    venv_path = module_config.get('venv')
    if not venv_path:
        print(f"ERROR: 'venv' path not provided in module configuration.", file=sys.stderr)
        return

    # Ensure the virtual environment exists or create it if it doesn't
    ensure_virtualenv(venv_path)

    # Call the Python executable directly from the virtual environment
    python_executable = os.path.join(venv_path, 'bin', 'python')

    # Construct the command to execute the blade server
    cmd = [
        python_executable, blade_path,
        "--topology", json.dumps(topology),
        "--blade", json.dumps(module_config)
    ]

    while True:
        print(f"INFO: Starting server {module_config['name']}.", file=sys.stdout)
        process = subprocess.Popen(cmd)
        process.wait()
        print(f"WARNING: Server {module_config['name']} terminated. Restarting...", file=sys.stderr)
        time.sleep(1)

def load_config(filepath):
    try:
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"ERROR: Cannot find configuration file at '{filepath}'.", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as exc:
        print(f"ERROR: Failed to parse YAML file '{filepath}'. Reason: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Multiple server manager")
    parser.add_argument("-c", "--config", type=str, default="example.yaml", help="Path to configuration YAML file")
    args = parser.parse_args()

    config = load_config(args.config)

    if not config or "modules" not in config:
        print(f"ERROR: Configuration file '{args.config}' is either empty or does not contain a 'modules' section.", file=sys.stderr)
        sys.exit(1)

    processes = []
    for module_config in config.get("modules", []):
        if module_config.get("managed", False):
            p = Process(target=run_blade_server, args=(module_config, config))
            p.start()
            processes.append(p)

    try:
        # Wait for all processes to complete
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("INFO: Keyboard interrupt received. Terminating processes.", file=sys.stderr)
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
    print("INFO: All server processes have been terminated.")


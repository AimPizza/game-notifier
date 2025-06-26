"""Installation of this tool."""

import subprocess
from pathlib import Path

SERVICE_DIR = Path.home() / '.config' / 'systemd' / 'user'
TEMPLATE_NAME = 'game-notifier@.service'
SERVICE_PATH = SERVICE_DIR / TEMPLATE_NAME

SERVICE_TEMPLATE = """\
[Unit]
Description=Gaming Notifier instance %I
After=network.target

[Service]
Type=simple
Environment="PATH={path_env}"
WorkingDirectory={cwd}
ExecStart=/usr/bin/env python3 {main_py} %I
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""


def write_template(main_py_path: Path):
    """Write service content into given path."""
    SERVICE_DIR.mkdir(parents=True, exist_ok=True)
    # Read the PATH from the current environment
    path_env = subprocess.check_output(['printenv', 'PATH'], text=True).strip()
    content = SERVICE_TEMPLATE.format(
        path_env=path_env,
        cwd=main_py_path.parent.parent,
        main_py=main_py_path,
    )
    SERVICE_PATH.write_text(content)
    print(f'Wrote service template to {SERVICE_PATH}')


def run_systemctl(cmd: str, *args):
    """Run a systemctl command as user."""
    full = ['systemctl', '--user', cmd, *args]
    print(f'> {" ".join(full)}')
    subprocess.run(full, check=True)


def setup_game_notifier_instance(config_dir: Path, main_py: Path):
    """Handle the installation flow.

    Takes two paths:
    - `config_dir`: to configuration (.env) for a specfic instance
    - `main_py`: to the main.py where this tool is installed
    """
    write_template(main_py)
    run_systemctl('daemon-reload')
    instance = config_dir.name
    run_systemctl('enable', '--now', f'game-notifier@{instance}')

    print('Service enabled and started.')

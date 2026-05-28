# ClusterPulse Project Structure

```
cluster_pulse/                          # Project root
│
├── .git/                               # Git repository (after init)
├── .gitignore                          # Git ignore rules
├── .gitattributes                      # Git attributes
├── .venv/                              # Python virtual environment (not tracked)
│
├── cluster_pulse/                      # Main package directory
│   │
│   ├── config.yaml                     # Template configuration (fallback)
│   ├── requirements.txt                # Python dependencies
│   ├── run.py                          # Application entrypoint
│   ├── README.md                       # User documentation
│   │
│   └── src/                            # Source code
│       ├── __init__.py
│       ├── config_loader.py            # Configuration loading logic
│       ├── scheduler.py                # Main polling loop and control listener
│       │
│       ├── clusters/                   # Cluster interaction module
│       │   ├── __init__.py
│       │   └── pbs_client.py           # PBS cluster SSH and qstat parsing
│       │
│       └── notifications/              # Notification providers
│           ├── __init__.py
│           ├── email_provider.py       # Email notification sender
│           └── ntfy_provider.py        # ntfy.sh notification sender and listener
│
├── project_struct.md                   # This file
└── [other repo files: LICENSE, etc.]
```

## File Descriptions

### Root Level
- `.gitignore` — Excludes `.venv/`, `*.pyc`, `__pycache__/`, build artifacts
- `.gitattributes` — Git text handling configuration
- `project_struct.md` — This project structure documentation

### cluster_pulse/
- `config.yaml` — Template configuration file (fallback if `~/.cluster_pulse.yaml` missing)
- `requirements.txt` — Python package dependencies (`paramiko`, `requests`, `pyyaml`)
- `run.py` — Main entry point; loads config and starts scheduler
- `README.md` — User-facing setup and usage guide
- `src/` — Implementation code

### src/
- `config_loader.py` — Loads configuration from home directory or fallback template
- `scheduler.py` — Main event loop; periodic polling and control command listener
- `clusters/` — PBS cluster client
- `notifications/` — Notification dispatch providers

### src/clusters/
- `pbs_client.py` — SSH connection to clusters, executes `qstat`, parses job output

### src/notifications/
- `email_provider.py` — Sends email notifications via SMTP
- `ntfy_provider.py` — Sends/receives ntfy.sh mobile push notifications

## Configuration
- `~/.cluster_pulse.yaml` — User's personal config (not in repo, outside workspace)
- Default fallback: `cluster_pulse/config.yaml`

## Runtime
- `python3 run.py` — Manual run (foreground)
- `systemctl --user start cluster_pulse` — Daemon mode (after systemd service setup)

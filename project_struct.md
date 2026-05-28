```
cluster_pulse/
│
├── config.yaml               # Your private configuration settings
├── requirements.txt          # Python dependencies
├── run.py                    # Entry point for the application
│
└── src/                      # Source code directory
    ├── __init__.py
    ├── config_loader.py      # Parses and validates config.yaml
    ├── scheduler.py          # Handles the timing loop/daemon logic
    │
    ├── clusters/             # Cluster communication module
    │   ├── __init__.py
    │   └── pbs_client.py     # Connects via SSH and parses qstat
    │
    └── notifications/        # Alerting module
        ├── __init__.py
        ├── email_provider.py # Handles SMTP mailing
        └── ntfy_provider.py  # Handles push notifications (optional/extra)
```
# ClusterPulse 🚀

Lightweight PBS cluster status monitor with SSH polling and `ntfy` mobile push notifications. Keeps credentials in `~/.cluster_pulse.yaml` outside the repository.

---

## Repository Layout

See [`project_struct.md`](../project_struct.md) for detailed file descriptions.

```text
cluster_pulse/
│
├── config.yaml              # Template config file (fallback only)
├── requirements.txt         # Python dependencies
├── run.py                   # Entrypoint for the application
└── src/                     # Runtime implementation
    ├── config_loader.py     # Loads config from home directory or fallback
    ├── scheduler.py         # Main polling loop and control listener
    ├── clusters/
    │   └── pbs_client.py    # SSH qstat execution and parsing
    └── notifications/
        ├── email_provider.py
        └── ntfy_provider.py
```

---

## Prerequisites

### Required packages

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv -y
```

### SSH access

ClusterPulse requires passwordless SSH login to your remote cluster. If you do not already have an SSH key pair, create one locally:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -C "cluster_pulse"
```

Copy the public key to your cluster account:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub your_username@cluster.example.com
```

Then confirm the connection works without a password prompt:

```bash
ssh -i ~/.ssh/id_ed25519 your_username@cluster.example.com "qstat -u your_username"
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url> /path/to/cluster_pulse
cd /path/to/cluster_pulse
```

### 2. Create and activate a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure ClusterPulse

Copy the template and customize:

```bash
cp config.yaml ~/.cluster_pulse.yaml
chmod 600 ~/.cluster_pulse.yaml
```

Edit `~/.cluster_pulse.yaml` with your cluster and notification settings.

---

## Configuration

```yaml
global:
  check_interval_seconds: 1800        # Periodic polling interval in seconds
  log_level: "INFO"                  # Logging verbosity

notifications:
  default_method: "ntfy"             # stdout, ntfy, email

  ntfy:
    topic: "your_unique_topic_name"  # Your ntfy topic for status notifications
    priority: "default"              # min, low, default, high, max
    control_topic: "your_control_topic_name"  # Optional command topic
    control_command: "check"          # Single command accepted by phone
    control_poll_interval_seconds: 15  # How often the app polls the control topic

  email:
    smtp_server: "smtp.example.com"
    port: 587
    sender: "your_email@example.com"
    password: "YOUR_EMAIL_PASSWORD_OR_TOKEN"
    receiver: "destination_email@example.com"

clusters:
  - name: "ClusterA"
    ip: "IP Address"
    username: "your_username"
    ssh_key_path: "~/.ssh/id_ed25519"

  - name: "ClusterB"
    ip: "IP Address"
    username: "your_username"
    ssh_key_path: "~/.ssh/id_ed25519"
```

### Notes on sensitive data

- Keep `~/.cluster_pulse.yaml` private and never commit it to version control.
- Do not store production passwords or access tokens in the repository.
- Use SSH keys rather than passwords for cluster access.
- If you use email notifications, prefer an application-specific password or token.

### Important: Daemon restart after changes

If you modify `~/.cluster_pulse.yaml` or any code in the repository, you must restart the daemon for the changes to take effect:

```bash
systemctl --user restart cluster_pulse
```

The running daemon does not automatically reload configuration. Similarly, if you pull code updates from the repository, always restart the service to load the new code.

### Notification modes

- `stdout` — print status to console only
- `ntfy` — easiest to use and currently the recommended mobile notification method
- `email` — available in config but not tested yet

Future interface support may include full email, Telegram, Slack, or other channels.

### Install and use the ntfy mobile app

1. Install `ntfy` app (Android: Google Play / F-Droid, iOS: App Store)
2. Subscribe to your `notifications.ntfy.topic` in the app
3. To send a control command: publish `check` to the topic (or `control_topic` if separate)
4. Responses appear as notifications in the app

### Phone-triggered control commands

- Send `check` to `control_topic` (or main `topic` if not configured) to trigger an immediate refresh
- The daemon responds with status results

---

## Running ClusterPulse

### Manual run

```bash
python3 run.py
```

### Run in the background with systemd

Create the service file at `~/.config/systemd/user/cluster_pulse.service`:

```ini
[Unit]
Description=ClusterPulse PBS Job Monitor
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/cluster_pulse
ExecStart=/path/to/cluster_pulse/.venv/bin/python /path/to/cluster_pulse/run.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user start cluster_pulse
systemctl --user enable cluster_pulse
systemctl --user status cluster_pulse
```

Stop the daemon now only:

```bash
systemctl --user stop cluster_pulse
```

This stops the currently running service but does not change whether it starts again after the next login/reboot. If the service is enabled, it will still start automatically the next time your user session begins.

Stop and prevent auto-start on restart/reboot:

```bash
systemctl --user stop cluster_pulse
systemctl --user disable cluster_pulse
systemctl --user status cluster_pulse
```

View logs:

```bash
journalctl --user -u cluster_pulse -f
```

---

## Troubleshooting

### Command not working from phone

- Ensure `python3 run.py` or the systemd service is running.
- Publish exactly `check` to the configured `control_topic`.
- If `control_topic` is missing, publish to the main `topic`.
- Verify the ntfy topic name is correct and unique.

### SSH key path errors

- Confirm the path in `ssh_key_path` exists locally.
- Use `~/.ssh/id_ed25519` or the correct path to your private key.
- Test manually with `ssh -i ~/.ssh/id_ed25519 user@cluster qstat -u user`.

### Configuration load order

- ClusterPulse prefers `~/.cluster_pulse.yaml`
- If the home file is missing, it falls back to `config.yaml` inside the repo

### Use safe permissions

```bash
chmod 600 ~/.cluster_pulse.yaml
```

---

## Notes

- Use a unique ntfy topic name to prevent other people from accidentally sending commands or receiving your notifications.
- Do not expose `control_topic` publicly unless you understand that it is effectively a remote trigger for the app.

---

## Acknowledgements

This package was developed with the assistance of GitHub Copilot.
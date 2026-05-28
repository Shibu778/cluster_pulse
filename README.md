Here is the complete, raw content for your `README.md` file. You can copy and paste this directly into your file:

```markdown
# ClusterPulse 🚀

ClusterPulse is a lightweight Linux utility that periodically polls PBS job status from one or more clusters over SSH, and delivers the results through a configurable notification pipeline.

It is designed to keep sensitive connection data out of the codebase by loading a per-user configuration file from `~/.cluster_pulse.yaml`.

---

## What ClusterPulse Provides

- periodic cluster status polling using `qstat`
- SSH-based cluster communication with private key authentication
- notification delivery via:
  - `stdout`
  - `ntfy`
  - `email`
- optional phone-triggered control commands
- safe per-user runtime configuration

---

## Repository Layout

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

ClusterPulse uses SSH keys for passwordless access. Confirm your cluster accepts your key:

```bash
ssh -i ~/.ssh/id_ed25519 your_username@cluster.example.com "qstat -u your_username"
```

If this succeeds without a password prompt, your SSH setup is ready.

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

ClusterPulse loads configuration from `~/.cluster_pulse.yaml` first. If that file is missing, it falls back to the repository template `config.yaml`.

Create your personal config file:

```bash
cp config.yaml ~/.cluster_pulse.yaml
chmod 600 ~/.cluster_pulse.yaml
```

Then edit `~/.cluster_pulse.yaml` and replace placeholder values with your own settings.

---

## Configuration

Use the following template and replace placeholders with your actual cluster and notification settings.

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
    ssh_key_path: "~/.ssh/id_rsa"

  - name: "ClusterB"
    ip: "IP Address"
    username: "your_username"
    ssh_key_path: "~/.ssh/id_rsa"
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
- `ntfy` — push to `ntfy.sh` using `topic`
- `email` — send email through SMTP

### Install and use the ntfy mobile app

1. Install the `ntfy` app on your phone:
   - Android: install from Google Play Store or F-Droid
   - iOS: install from the App Store

2. Open the app and subscribe to your configured topic:
   - Topic name: the value of `notifications.ntfy.topic`
   - Example: `your_unique_topic_name`

3. To receive alerts, make sure notifications are enabled for the app.

4. To send a control command from the phone:
   - Use the same `control_topic` if configured, otherwise use the main `topic`
   - Publish the exact text `check`
   - In the app, use the message composition field and send `check`

5. Confirm the command was accepted by checking for the acknowledgement notification.

6. If using a shared or public topic, choose a unique topic name to avoid collisions.

### Phone-triggered control commands

If `control_topic` is configured, ClusterPulse polls that topic for a single command.

- Command text accepted: `check`
- Publish `check` to the control topic from your phone to trigger an immediate refresh
- The application sends an acknowledgement message back to the same topic

If `control_topic` is not provided, the main `topic` is used for command polling.

---

## Running ClusterPulse

### Manual run

Start it in the current terminal:

```bash
python3 run.py
```

If you want phone-triggered refresh, make sure the process is running before publishing `check`.

### Run in the background with systemd

Create the user service directory:

```bash
mkdir -p ~/.config/systemd/user/
```

Create `~/.config/systemd/user/cluster_pulse.service` with:

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
- Use `~/.ssh/id_rsa` or the correct path to your private key.
- Test manually with `ssh -i ~/.ssh/id_rsa user@cluster qstat -u user`.

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

```

```
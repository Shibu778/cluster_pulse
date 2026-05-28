import json
import requests
import textwrap


def _format_for_phone(body_content, width=48):
    """Wrap long lines so the notification is easier to read on a small phone screen."""
    wrapped_lines = []
    for line in body_content.splitlines():
        if not line.strip():
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(line, width=width, replace_whitespace=False))
    return "\n".join(wrapped_lines)


def send_ntfy_push(config, subject, body_content, topic_override=None):
    """
    Sends a POST request to ntfy.sh to trigger an instant mobile push notification.
    """
    # Safeguard against missing configuration blocks
    if 'ntfy' not in config['notifications']:
        print("❌ Error: 'ntfy' configuration block missing in config file.")
        return

    ntfy_config = config['notifications']['ntfy']
    topic = topic_override or ntfy_config.get('topic')
    
    if not topic:
        print("❌ Error: ntfy 'topic' is not specified in the configuration.")
        return

    # Build the target URL endpoint
    url = f"https://ntfy.sh/{topic}"
    body_content = _format_for_phone(body_content)
    
    # HTTP Headers configure metadata like titles and priority inside the mobile app
    headers = {
        "Title": subject,
        "Priority": ntfy_config.get("priority", "default"),
        "Tags": "computer,bell"  # Adds clean decorative emojis to your mobile alert
    }
    
    try:
        # Send the wrapped text body data as the POST request body
        response = requests.post(url, data=body_content, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print(f"📱 Mobile push alert successfully dispatched via ntfy to topic: {topic}")
        else:
            print(f"❌ ntfy server returned an error code: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Failed to reach ntfy server endpoint: {e}")


def _parse_ntfy_json_lines(text):
    messages = []
    for raw_line in text.splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            payload = json.loads(raw_line)
        except Exception:
            continue
        if payload.get('event') != 'message':
            continue
        messages.append(payload)
    return messages


def poll_ntfy_commands(config, last_seen_id=None):
    """Poll the ntfy control topic for new command messages."""
    if 'ntfy' not in config['notifications']:
        return [], last_seen_id

    ntfy_config = config['notifications']['ntfy']
    control_topic = ntfy_config.get('control_topic') or ntfy_config.get('topic')
    if not control_topic:
        return [], last_seen_id

    params = {
        'poll': '1',
    }

    if last_seen_id is None:
        params['since'] = 'latest'
    else:
        params['since'] = last_seen_id

    url = f"https://ntfy.sh/{control_topic}/json"

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to poll ntfy control topic {control_topic}: {response.status_code}")
            return [], last_seen_id

        messages = _parse_ntfy_json_lines(response.text)
        command_texts = []
        latest_id = last_seen_id
        for msg in messages:
            message_id = msg.get('id')
            if message_id:
                latest_id = message_id
            command_texts.append(msg.get('message', '').strip())

        return command_texts, latest_id
    except Exception as e:
        print(f"❌ Failed to poll ntfy control topic: {e}")
        return [], last_seen_id

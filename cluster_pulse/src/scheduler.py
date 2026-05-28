import time
import threading
from src.clusters.pbs_client import PBSClusterClient
from src.notifications.email_provider import send_email
from src.notifications.ntfy_provider import send_ntfy_push, poll_ntfy_commands

def run_pulse_cycle(config):
    print("\n⏰ ClusterPulse waking up...")
    report_data = []
    
    # 1. Fetch data from all configured clusters
    for cluster_info in config['clusters']:
        print(f"Checking cluster: {cluster_info['name']}...")
        client = PBSClusterClient(
            name=cluster_info['name'],
            ip=cluster_info['ip'],
            username=cluster_info['username'],
            ssh_key_path=cluster_info['ssh_key_path']
        )
        status = client.fetch_job_status()
        
        report_data.append(f"=== {cluster_info['name']} ===")
        report_data.append(status)
        report_data.append("\n" + "="*30 + "\n")

    # 2. Combine reports and dispatch via notification rule
    final_report = "\n".join(report_data)
    method = config['notifications'].get('default_method', 'stdout')
    if method == 'email':
        send_email(config, "ClusterPulse: Your PBS Job Status Report", final_report)
    elif method == 'ntfy':
        send_ntfy_push(config, "ClusterPulse Alert", final_report)
    else:
        print(final_report)  # Fallback to console print

    return final_report


def _command_matches(command, allowed_command):
    if not command:
        return False

    normalized = command.strip().lower()
    if isinstance(allowed_command, str):
        return normalized == allowed_command.strip().lower()
    if isinstance(allowed_command, (list, tuple, set)):
        return any(normalized == str(allowed).strip().lower() for allowed in allowed_command)
    return False


def _run_control_listener(config, stop_event, lock):
    ntfy_config = config['notifications'].get('ntfy', {})
    control_topic = ntfy_config.get('control_topic') or ntfy_config.get('topic')
    if not control_topic:
        return

    poll_interval = ntfy_config.get('control_poll_interval_seconds', 15)
    control_command = ntfy_config.get('control_command', 'check')
    last_seen_id = None
    initial_pass = True

    print(f"🔁 ntfy control listener enabled on topic: {control_topic}")
    while not stop_event.is_set():
        command_texts, last_seen_id = poll_ntfy_commands(config, last_seen_id)
        if initial_pass:
            initial_pass = False
        else:
            for command_text in command_texts:
                if _command_matches(command_text, control_command):
                    print(f"📲 ntfy control command received: {command_text}")
                    with lock:
                        report = run_pulse_cycle(config)
                    
                    # Skip acknowledgement if control_topic and main topic are identical
                    # to avoid sending redundant messages to the same topic
                    main_topic = ntfy_config.get('topic')
                    if control_topic != main_topic:
                        ack_body = (
                            f"Command received: {command_text}\n"
                            f"Triggered immediate status check.\n\n"
                            f"Status summary:\n{report}"
                        )
                        send_ntfy_push(
                            config,
                            subject="ClusterPulse command accepted",
                            body_content=ack_body,
                            topic_override=control_topic,
                        )
                    break

        time.sleep(poll_interval)


def start_scheduler(config):
    interval = config['global'].get('check_interval_seconds', 1800)
    print(f"🚀 ClusterPulse initialized. Checking every {interval} seconds.")

    stop_event = threading.Event()
    cycle_lock = threading.Lock()
    control_thread = threading.Thread(
        target=_run_control_listener,
        args=(config, stop_event, cycle_lock),
        daemon=True,
    )
    control_thread.start()

    try:
        while True:
            with cycle_lock:
                run_pulse_cycle(config)
            print(f"💤 Going to sleep for {interval} seconds...")
            time.sleep(interval)
    except KeyboardInterrupt:
        stop_event.set()
        print("\n👋 ClusterPulse shutting down cleanly.")
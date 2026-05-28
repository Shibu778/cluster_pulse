import os
import yaml
import shutil

def load_config():
    """
    Looks for the primary configuration file in the user's home directory.
    If missing, it attempts to use the project directory's template config.yaml.
    """
    # 1. Define paths: Home directory primary vs local fallback template
    home_config_path = os.path.expanduser("~/.cluster_pulse.yaml")
    local_template_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    
    selected_path = None

    # 2. Resolve which file to read
    if os.path.exists(home_config_path):
        selected_path = home_config_path
    elif os.path.exists(local_template_path):
        print(f"⚠️ Personal configuration missing at {home_config_path}.")
        print(f"ℹ️ Falling back to local template repository: {local_template_path}")
        selected_path = local_template_path
    else:
        raise FileNotFoundError(
            f"Critical Error: No configuration found at {home_config_path} "
            f"or template file at {local_template_path}"
        )

    # 3. Read and parse the YAML payload
    with open(selected_path, 'r') as file:
        config = yaml.safe_load(file)
        
    # 4. Standardize platform key paths (~ expansion)
    if 'clusters' in config and config['clusters']:
        for cluster in config['clusters']:
            if 'ssh_key_path' in cluster and cluster['ssh_key_path']:
                cluster['ssh_key_path'] = os.path.expanduser(cluster['ssh_key_path'])
            
    return config
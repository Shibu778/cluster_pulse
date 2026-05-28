import paramiko
import os

class PBSClusterClient:
    def __init__(self, name, ip, username, ssh_key_path):
        self.name = name
        self.ip = ip
        self.username = username
        self.ssh_key_path = ssh_key_path

    def _parse_qstat_output(self, output):
        """Parse qstat output and return each job as a vertical label/value block."""
        lines = output.splitlines()
        parsed_rows = []
        header_found = False
        headers = []

        for line in lines:
            if not header_found:
                if line.startswith("Job ID") or ("Job" in line and "Queue" in line and "Time" in line and "S" in line):
                    header_found = True
                    tokens = line.split()
                    normalized = []
                    req_label_used = False
                    for idx, token in enumerate(tokens):
                        if token == "Job" and idx + 1 < len(tokens) and tokens[idx + 1] == "ID":
                            normalized.append("JobID")
                            continue
                        if token == "ID" and idx > 0 and tokens[idx - 1] == "Job":
                            continue
                        if token == "Time":
                            if not req_label_used:
                                normalized.append("Req'd")
                                req_label_used = True
                            else:
                                normalized.append("Elap")
                        elif token == "S":
                            normalized.append("Stat")
                        else:
                            normalized.append(token)
                    headers = normalized
                continue

            if not line.strip() or line.startswith("-"):
                continue

            parts = line.split()
            if not headers or len(parts) < len(headers):
                continue

            fields = []
            for idx, header in enumerate(headers):
                value = parts[idx] if idx < len(parts) else ""
                fields.append(f"{header}: {value}")

            parsed_rows.append("\n".join(fields))

        if not parsed_rows:
            return f"[{self.name}] No active jobs found."

        return "\n\n".join(parsed_rows)

    def fetch_job_status(self):
        """Connects to the cluster and returns the raw/parsed qstat output."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Connect using private key
            ssh.connect(
                hostname=self.ip, 
                username=self.username, 
                key_filename=self.ssh_key_path,
                timeout=15
            )
            
            # Execute qstat targeting the current user
            stdin, stdout, stderr = ssh.exec_command(f"qstat -u {self.username}")
            
            error = stderr.read().decode('utf-8')
            if error:
                return f"[{self.name}] Error running qstat: {error}"
            
            output = stdout.read().decode('utf-8')
            if not output.strip():
                return f"[{self.name}] No active jobs found."
            return self._parse_qstat_output(output)
            
        except Exception as e:
            return f"[{self.name}] Connection failed: {str(e)}"
        finally:
            ssh.close()
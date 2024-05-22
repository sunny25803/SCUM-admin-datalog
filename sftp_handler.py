import os
import paramiko
from datetime import datetime, timedelta

def download_sftp_file(ftp_host, ftp_user, ftp_pass, remote_file_path, local_file_path, port=8822):
    try:
        transport = paramiko.Transport((ftp_host, port))
        transport.connect(username=ftp_user, password=ftp_pass)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_file_path, local_file_path)
        sftp.close()
        transport.close()
    except Exception as e:
        raise Exception(f"SFTP download failed: {e}")

def is_recent(file_attr, hours=3):
    """Check if the given file attribute's modification time is within the last 'hours' hours."""
    file_time = datetime.fromtimestamp(file_attr.st_mtime)
    return file_time >= datetime.now() - timedelta(hours=hours)

def download_sftp_log_files(ftp_host, ftp_user, ftp_pass, remote_folder_path, local_folder_path, port=8822, hours=3):
    try:
        transport = paramiko.Transport((ftp_host, port))
        transport.connect(username=ftp_user, password=ftp_pass)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)
        
        remote_files = sftp.listdir(remote_folder_path)
        
        for file in remote_files:
            if file.endswith('.log'):
                try:
                    file_attr = sftp.stat(os.path.join(remote_folder_path, file))
                    if is_recent(file_attr, hours):
                        local_file_path = os.path.join(local_folder_path, file)
                        sftp.get(os.path.join(remote_folder_path, file), local_file_path)
                except Exception as e:
                    print(f"Failed to retrieve modification time for {file}: {e}")
        
        sftp.close()
        transport.close()
    except Exception as e:
        raise Exception(f"SFTP download failed: {e}")

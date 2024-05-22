import os
from ftplib import FTP
from datetime import datetime, timedelta

def download_file(ftp_host, ftp_user, ftp_pass, remote_file_path, local_file_path, port=21):
    try:
        ftp = FTP()
        ftp.connect(ftp_host, port)
        ftp.login(user=ftp_user, passwd=ftp_pass)
        with open(local_file_path, 'wb') as local_file:
            ftp.retrbinary('RETR ' + remote_file_path, local_file.write)
        ftp.quit()
    except Exception as e:
        raise Exception(f"FTP download failed: {e}")

def is_recent(modified_time_str, hours=3):
    """Check if the given modified time string (format: '%Y%m%d%H%M%S') is within the last 'hours' hours."""
    file_time = datetime.strptime(modified_time_str, '%Y%m%d%H%M%S')
    return file_time >= datetime.now() - timedelta(hours=hours)

def download_log_files(ftp_host, ftp_user, ftp_pass, remote_folder_path, local_folder_path, port=21, hours=3):
    try:
        ftp = FTP()
        ftp.connect(ftp_host, port)
        ftp.login(user=ftp_user, passwd=ftp_pass)
        
        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)
        
        ftp.cwd(remote_folder_path)
        remote_files = ftp.nlst()
        
        for file in remote_files:
            if file.endswith('.log'):
                try:
                    # Get the modification time of the remote file
                    modified_time = ftp.sendcmd(f'MDTM {file}')[4:].strip()
                    if is_recent(modified_time, hours):
                        local_file_path = os.path.join(local_folder_path, file)
                        with open(local_file_path, 'wb') as local_file:
                            ftp.retrbinary('RETR ' + file, local_file.write)
                except Exception as e:
                    print(f"Failed to retrieve modification time for {file}: {e}")
        
        ftp.quit()
    except Exception as e:
        raise Exception(f"FTP download failed: {e}")

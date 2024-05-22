import os
from ftp_handler import download_log_files
from sftp_handler import download_sftp_log_files

def download_and_open_files(protocol, ftp_host, ftp_user, ftp_pass, port, game_port, remote_folder_path):
    try:
        local_folder_path = os.path.join(os.getcwd(), f"{ftp_host}_{game_port}_Logs")
        if protocol == "FTP":
            download_log_files(ftp_host, ftp_user, ftp_pass, remote_folder_path, local_folder_path, port, hours=3)
        elif protocol == "SFTP":
            download_sftp_log_files(ftp_host, ftp_user, ftp_pass, remote_folder_path, local_folder_path, port, hours=3)
        return local_folder_path
    except Exception as e:
        raise Exception(f"下载和打开文件失败: {e}")
def load_local_files(local_folder_path):
    try:
        # 实现读取本地文件的逻辑，例如加载日志文件并返回其内容
        files = os.listdir(local_folder_path)
        log_files = [f for f in files if f.endswith('.log')]
        log_contents = []
        for log_file in log_files:
            with open(os.path.join(local_folder_path, log_file), 'r', encoding='utf-8') as file:
                log_contents.append(file.read())
        return log_contents
    except Exception as e:
        raise Exception(f"加载本地文件失败: {e}")
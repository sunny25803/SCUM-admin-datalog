import json
import os
import sys

CONFIG_DIR = 'configs'
CONFIG_LIST_FILE = 'config_list.json'

def get_base_path():
    # 使用 sys.argv[0] 获取可执行文件的实际路径
    base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    print(f"Base path: {base_path}")  # 调试信息
    return base_path

def get_full_path(relative_path):
    full_path = os.path.join(get_base_path(), relative_path)
    print(f"Full path for {relative_path}: {full_path}")  # 调试信息
    return full_path

def save_config(name, config):
    config_dir = get_full_path(CONFIG_DIR)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    config_path = os.path.join(config_dir, f"{name}.json")
    with open(config_path, 'w') as f:
        json.dump(config, f)
    update_config_list(name)

def load_config(name):
    config_path = os.path.join(get_full_path(CONFIG_DIR), f"{name}.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def update_config_list(name=None):
    config_list_path = get_full_path(CONFIG_LIST_FILE)
    config_dir = get_full_path(CONFIG_DIR)
    config_files = [os.path.splitext(f)[0] for f in os.listdir(config_dir) if f.endswith('.json')]

    if not os.path.exists(config_list_path):
        with open(config_list_path, 'w') as f:
            json.dump([], f)
    
    with open(config_list_path, 'r') as f:
        config_list = json.load(f)
    
    if name and name not in config_list:
        config_list.append(name)
    else:
        config_list = config_files

    with open(config_list_path, 'w') as f:
        json.dump(config_list, f)

def get_config_list():
    config_list_path = get_full_path(CONFIG_LIST_FILE)
    if os.path.exists(config_list_path):
        with open(config_list_path, 'r') as f:
            return json.load(f)
    return []

def delete_config(name):
    config_path = os.path.join(get_full_path(CONFIG_DIR), f"{name}.json")
    if os.path.exists(config_path):
        os.remove(config_path)
    update_config_list()

def set_working_directory():
    os.chdir(get_base_path())
    print(f"Working directory set to: {os.getcwd()}")  # 调试信息

if __name__ == '__main__':
    set_working_directory()
    print("配置文件列表:", get_config_list())

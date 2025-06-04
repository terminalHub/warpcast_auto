import subprocess
from config.config import LDPLAYER_PATH

def launch_instance(index: int):
    return subprocess.run([LDPLAYER_PATH, "launch", "--index", str(index)])
def stop_instance(index: int):
    return subprocess.run([LDPLAYER_PATH, "quit", "--index", str(index)])

def list_instances():
    result = subprocess.run([LDPLAYER_PATH, "list2"], capture_output=True, text=True)
    return result.stdout

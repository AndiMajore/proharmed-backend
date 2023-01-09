import os
from datetime import date

def get_version():
    version = None
    version_file = "/usr/src/mesidha/mapping_files/version"
    if os.path.exists(version_file):
        with open(version_file) as fh:
            version = fh.readline().strip()
    # if version is None:
    #     save_version()
    #     version = get_version()
    return version

def save_version():
    with open("/usr/src/mesidha/mapping_files/version",'w') as fh:
        fh.write(date.today().isoformat())
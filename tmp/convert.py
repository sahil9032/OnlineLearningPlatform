import os
import subprocess

from onlinelearningplatform import settings


def convert(in_path, out_path, height):
    cmd = ['ffmpeg', '-i', in_path, '-vf', 'scale=-2:' + height, '-c:v',
           'libx264', '-preset', 'fast', '-c:a', 'copy', out_path]
    cmd = ' '.join(cmd)
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=os.path.join(
        settings.BASE_DIR, 'tmp'), shell=True)
    output, error = p.communicate()
    return p.returncode

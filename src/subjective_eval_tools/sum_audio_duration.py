'''
How long does it take to listen to all your audio?  
Sums the total duration of all audio files in a directory.  
'''

import os

def getDuration(filename: str):
    duration = os.popen(
        'ffprobe -v error -show_entries '
        'format=duration -of '
        'default=noprint_wrappers=1:nokey=1 ' + 
        filename, 
    ).read()
    return float(duration)

def walkDirAndPrintDurationStats(
    root_dir: str, 
    known_ext: tuple[str, ...] = ('wav', 'mp3'),
):
    total_duration = 0
    print()
    for dirpath, _, filenames in os.walk(root_dir):
        dir_duration = 0.0
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.strip('.').lower() in known_ext:
                dir_duration += getDuration(os.path.join(dirpath, filename))
        if dir_duration > 0.0:
            print(dirpath, '\t', format(
                dir_duration / 60, '.1f', 
            ), 'min')
        total_duration += dir_duration
    print()
    print(f'Total duration: {total_duration / 60 :.1f} min')

if __name__ == '__main__':
    walkDirAndPrintDurationStats('.')

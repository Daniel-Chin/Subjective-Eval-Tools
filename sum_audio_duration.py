'''
How long does it take to listen to all your audio?  
'''

import os
import argparse

KNOWN_EXT = ['mp3']

def parseArgs():
    parser = argparse.ArgumentParser(description='Sum audio duration.')
    parser.add_argument(
        '--root', help='Input root folder of audio files', 
        type=str, required=True, 
    )
    root: str = parser.parse_args().root
    return root

def main():
    root = parseArgs()
    total_duration = 0
    print()
    for dirpath, _, filenames in os.walk(root):
        dir_duration = 0.0
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.strip('.').lower() in KNOWN_EXT:
                duration = os.popen(
                    'ffprobe -v error -show_entries '
                    'format=duration -of '
                    'default=noprint_wrappers=1:nokey=1 ' + 
                    os.path.join(dirpath, filename), 
                ).read()
                dir_duration += float(duration)
        if dir_duration > 0.0:
            print(dirpath, '\t', format(
                dir_duration / 60, '.1f', 
            ), 'min')
        total_duration += dir_duration
    print()
    print(f'Total duration: {total_duration / 60 :.1f} min')

if __name__ == '__main__':
    main()

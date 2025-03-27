'''
The anonymized names are salted hashes. Even if you lose the lookup table, as long as you keep the salt as well as the pre-anonymized filenames, everything can be recovered.  
About the salt:  
- I recommend using a short word that you can remember.  
- Keep the salt file around.  
- Cryptographically, as long as the survey respondents don't know the salt, they can't deanonymize.  
- An additional benefit is you can re-run the script and the correspondence won't change. (e.g. No need to re-upload to SoundCloud)  

This script assumes certain dir structure of the src folder. Modify code after the "# modify" tag if needed.  
'''

import os
from os import path
import sys
import json
import shutil
import argparse
import hashlib

CODE_LENGTH = 4

def parseArgs():
    parser = argparse.ArgumentParser(description='Anonymize audio files.')
    parser.add_argument(
        '--src', help='Input source folder of audio files', 
        type=str, required=True, 
    )
    parser.add_argument(
        '--salt', help='Input salt file, containing a raw string in ascii.', 
        type=str, required=True, 
    )
    parser.add_argument(
        '--dest', help='Output folder of anonymized files.', 
        type=str, required=True, 
    )
    parser.add_argument(
        '--lookup', help='Output lookup file.', 
        type=str, required=True, 
    )
    args = parser.parse_args()
    src: str = args.src
    salt: str = args.salt
    dest: str = args.dest
    lookup: str = args.lookup
    return src, salt, dest, lookup

def askConfirm():
    if input('y/n >').lower() != 'y':
        print('aborted')
        sys.exit(1)

def main():
    src, salt_filename, dest, lookup_filename = parseArgs()
    if path.exists(dest):
        print('Warning: destination folder already exists. Overwrite?')
        askConfirm()
        shutil.rmtree(dest)
    os.makedirs(dest, exist_ok=False)
    if path.isfile(lookup_filename):
        print('Warning: anonymization lookup file already exists. Overwrite?')
        print('This is a dangerous operation!!!')
        askConfirm()
    with open(salt_filename, 'r') as f:
        salt = f.read().strip()
    lookup = []
    used_ano_names = set()

    # modify
    # handle the dir structure of src folder.

    # for task in os.listdir(src):
    for task in '.':

        filenames = os.listdir(path.join(src, task))
        filenames.sort()
        for filename in filenames:
            stem, ext = path.splitext(filename)
            task_, song_name, model = stem.split('-')
            assert task == task_
            hash_code = hashlib.sha256(f'{filename}{salt}'.encode()).hexdigest()
            anonymized = f's_{hash_code[:CODE_LENGTH]}{ext}'
            if anonymized in used_ano_names:
                raise ValueError(f'Hash collision! Increase `CODE_LENGTH` and try again.')
            used_ano_names.add(anonymized)
            shutil.copy(path.join(src, task, filename), path.join(dest, anonymized))
            lookup.append((
                anonymized, task, song_name, model, 
            ))
    with open(lookup_filename, 'w') as f:
        json.dump(lookup, f, indent=2)
    print('ok')

if __name__ == '__main__':
    main()

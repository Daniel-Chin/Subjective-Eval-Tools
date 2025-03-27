'''
The anonymized names are salted hashes. You must keep the salt as well as the pre-anonymized filenames, so that everything can be recovered.  
About the salt:  
- I recommend using a short word that you can remember.
- Keep the salt file around.  
- Cryptographically, as long as the survey respondents don't know the salt, they can't deanonymize.  
- Realistically, no one is gonna try to deanonymize. Just use an simple, easy-to-remember salt.  
- An additional benefit is you can re-run the script and the correspondence won't change. (e.g. No need to re-upload to SoundCloud)  
'''

import typing as tp
import os
from os import path
import sys
import json
import shutil
import argparse
import hashlib

def parseArgs():
    # deprecated
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

def anonymize(
    root_dir: str,
    source_filenames: tp.Iterable[str],
    salt: str,
    destination_dirname: str,
    index_filename: str,
    code_length: int = 4,
):
    '''
    `root_dir`: The root of your project dir. Important! `root_dir` shouldn't change, otherwise the hash will change.
    `source_filenames`: A list of filenames (can be in multiple dirs) relative to `root_dir`. The order should be what would appear on the survey, from the editor's view.  
    `destination_dirname`: Relative to `root_dir`. Where to put the anonymized files.
    `index_filename`: Relative to `root_dir`. Where to output the index file, which will be used by other tools.
    `code_length`: How many digits in the anonymized filename. 
    '''
    abs_dest = path.join(root_dir, destination_dirname)
    if path.exists(abs_dest):
        print('Warning: destination dir already exists. Overwrite?')
        askConfirm()
        shutil.rmtree(abs_dest)
    os.makedirs(abs_dest)
    abs_index = path.join(root_dir, index_filename)
    if path.isfile(abs_index):
        print('Warning: index file already exists. Overwrite?')
        print('This can be a dangerous operation!!!')
        askConfirm()
    index = []
    used_ano_names = set()

    for source_filename in source_filenames:
        abs_src = path.abspath(path.join(root_dir, source_filename))
        # make source_filename canonical relative to root_dir
        source_filename = path.relpath(abs_src, root_dir)
        _, ext = path.splitext(source_filename)
        hash_code = hashlib.sha256(f'{salt}{source_filename}'.encode()).hexdigest()
        anonymized = f's_{hash_code[:code_length]}'
        if anonymized in used_ano_names:
            raise ValueError(f'Hash collision! Increase `CODE_LENGTH` and try again.')
        used_ano_names.add(anonymized)
        shutil.copy(abs_src, path.join(abs_dest, anonymized + ext))
        index.append((
            anonymized, source_filename, 
        ))
    with open(abs_index, 'w') as f:
        json.dump(index, f, indent=2)
    print('ok')

'''
A tool for batch copying embed html code from soundcloud.  
It controls your keyboard to do that.  
You need the Vimium extension in your browser.  

To copy:  
1. Open your album (list of audios) page in soundcloud.  
2. Press ` in your browser to start the automated GUI sequence.  
2.1. Correction! You need to press Enter in the terminal instead. See comments in code.  
3. Wait for the browser to return to the original state.  
4. Finished. You can now paste.  

To abort during automation: Press `  

Additional notes:  
- This setup is necessary because SoundCloud's embed html of a private song contains a secret token.  
- Recommended workflow: edit the questions in the survey one by one. For each edit, evoke this tool once to copy the next song's embed code.  
- You likely need to modify code around "# modify"  
- An observed issue: sometimes the "Your track isn’t eligible for recommendation yet." banner unpredictably doesn't show, affecting vimium key maps. You'd have to manually do those ones.  
'''

import typing as tp
import os
import json
import threading
import time
import argparse

import keyboard

SHORT_DELAY = 0.1
WEBPAGE_LOAD_DELAY = 1

def parseArgs():
    parser = argparse.ArgumentParser(description='Automate copying embed html code from soundcloud.')
    parser.add_argument(
        '--index', help='The index json file previously generated.', 
        type=str, required=True,
    )
    parser.add_argument(
        '--skip_to', help='Skip to a certain filename.', 
        type=str, 
    )
    args = parser.parse_args()
    index: str = args.index
    skip_to: str | None = args.skip_to
    return index, skip_to

def Samples(index_filename: str):
    with open(index_filename, 'r') as f:
        index = json.load(f)
    
    for anonymized, source_filename in index:
        anonymized: str
        source_filename: str
        yield anonymized, source_filename

def main(index_filename: str, skip_to: str | None):
    print(__doc__)

    do_abort = False
    def abort():
        nonlocal do_abort
        do_abort = True
    
    is_during_automation = False
    barrier = threading.Lock()
    barrier.acquire()

    # register the hotkey
    def onHotKey():
        time.sleep(0.1)
        print(f'{is_during_automation = }')
        if is_during_automation:
            abort()
        else:
            barrier.release()

    def sleep(n_sec: float | int):
        time.sleep(n_sec)
        if do_abort:
            raise EOFError('aborted')
    
    skip_done = skip_to is None
    keyboard.add_hotkey('`', onHotKey)
    try:
        print('Awaiting input...')
        for anonymized, source_filename in Samples(index_filename):
            if not skip_done:
                assert skip_to is not None
                if skip_to in anonymized:
                    skip_done = True
                else:
                    print('skipping:', anonymized)
                    continue
            print('next up:', anonymized, source_filename)

            # hotkey isn't working on my machine... Switching to manual
            # barrier.acquire()
            input('Press enter to continue...')

            is_during_automation = True

            sleep(1)
            keyboard.send('end')    # go to end of list
            sleep(WEBPAGE_LOAD_DELAY)
            keyboard.send('ctrl+f') # browser search bar
            sleep(SHORT_DELAY)
            stem, _ = os.path.splitext(anonymized)
            keyboard.write(         # song title
                stem.split('_')[-1]  # https://github.com/boppreh/keyboard/issues/434
            )
            sleep(SHORT_DELAY)
            keyboard.send('enter')  # focus on search hit
            sleep(SHORT_DELAY)
            keyboard.send('esc')    # exit search bar
            sleep(SHORT_DELAY)
            keyboard.send('enter')  # go to song page
            sleep(WEBPAGE_LOAD_DELAY)
            # keyboard.send('page down')  # depends on your window height. I need this to get the "share" button in the view.  
            # sleep(0.5)
            if 1:
                keyboard.write('f', delay=SHORT_DELAY)  # vimium
                sleep(0.7)
                # sleep(1)    # for debug
                # select "share" button
                keyboard.write('j', delay=SHORT_DELAY) # modify. this code may change, depending on your window height.  
            else:
                sleep(2)    # the human should click the button now
            sleep(0.7)
            keyboard.write('fc', delay=SHORT_DELAY) # vimium. select "embed"
            sleep(0.5)
            for _ in range(4):
                keyboard.send('tab')    # cycle to the code textbox
                sleep(SHORT_DELAY)
            keyboard.send('ctrl+c')     # copy
            sleep(SHORT_DELAY)
            keyboard.send('alt+left')   # back to album page
            sleep(0.3)
            keyboard.send('f5')         # refresh

            is_during_automation = False
    finally:
        keyboard.remove_all_hotkeys()
    print('ok')

if __name__ == '__main__':
    index_filename, skip_to = parseArgs()
    main(index_filename, skip_to)

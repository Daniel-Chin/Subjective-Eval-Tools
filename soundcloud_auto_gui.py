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
'''

import typing as tp
import os
import json
import threading
import time

import keyboard

SKIP_TO: str | None = None  # anonymized filename

SHORT_DELAY = 0.1
WEBPAGE_LOAD_DELAY = 1

def Samples():
    # modify this function to your need.
    with open('anonymization_lookup.json', 'r') as f:
        lookup = json.load(f)
    
    for filename, task, song, model in lookup:
        filename: str
        task: str
        song: str
        model: str
        yield filename, task, song, model

def Pages():
    # modify this function to your need.
    samples = Samples()
    current_page = None
    acc = []
    while True:
        try:
            filename, task, song, model = next(samples)
        except StopIteration:
            yield tuple(acc)
            break
        if current_page is None:
            current_page = (task, song)
            acc.append((filename, task, song, model))
        else:
            if current_page == (task, song):
                acc.append((filename, task, song, model))
            else:
                yield tuple(acc)
                acc = [(filename, task, song, model)]
                current_page = (task, song)

def unitTestPages():
    a = [*Samples()]
    b = []
    for page in Pages():
        b.extend(page)
    assert a == b

def SortedPages():
    # place the prompt at the top.
    for page in Pages():
        sorted_page: tp.List[tp.Tuple[str, str, str, str]] = []
        for filename, task, song, model in page:
            if model == 'prompt':
                sorted_page.insert(0, (filename, task, song, model))
            else:
                sorted_page.append((filename, task, song, model))
        yield sorted_page

def inspectSortedPages():
    for page in SortedPages():
        for filename, task, song, model in page:
            print(filename, task, song, model)
        input()

def main():
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
    
    skip_done = SKIP_TO is None
    keyboard.add_hotkey('`', onHotKey)
    try:
        print('Awaiting input...')
        for page in SortedPages():
            print('new page:', page[0][1], page[0][2])
            for filename, _, _, _ in page:
                if not skip_done:
                    assert SKIP_TO is not None
                    if SKIP_TO in filename:
                        skip_done = True
                    else:
                        print('skipping:', filename)
                        continue
                print('next up:', filename)

                # hotkey isn't working on my machine... Switching to manual
                # barrier.acquire()
                input('Press enter to continue...')

                is_during_automation = True

                sleep(1)
                keyboard.send('end')    # go to end of list
                sleep(WEBPAGE_LOAD_DELAY)
                keyboard.send('ctrl+f') # browser search bar
                sleep(SHORT_DELAY)
                stem, _ = os.path.splitext(filename)
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
                keyboard.send('page down')  # depends on your window height. I need this to get the "share" button in the view.  
                sleep(0.5)
                keyboard.write('f', delay=SHORT_DELAY)  # vimium
                sleep(0.5)
                # sleep(1)    # for debug
                # select "share" button
                keyboard.write('af', delay=SHORT_DELAY) # this code may change.
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
    unitTestPages()
    # inspectSortedPages()
    main()

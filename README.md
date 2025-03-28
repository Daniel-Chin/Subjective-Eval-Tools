# Subjective Evaluation Tools
This repo helps you with Music AI subjective evaluation surveys.  
- Deterministic filename anonymization (salted hash).  
- Batch copy embed codes from Soundcloud.  
- Summarize audio durations.  

## Install
- No need to pull or clone this repo.  
- Use `uv` to manage your project. 
  - In your project dir, `uv init`  
- `uv add git+https://github.com/Daniel-Chin/Subjective-Eval-Tools/`  

## Usage
### Anonymize filenames
```python
from subjective_eval_tools import anonymize

def MySamples():
    for task in [...]:
        for model in [...]:
            yield f'./{task}/{model}.mp3'

anonymize.anonymize(
    root_dir='.', 
    source_filenames=MySamples(),
    salt='banana',
    destination_dirname='./anonymized/',
    index_filename='./index.json',
)
```

### Sum audio durations
```bash
uv run python -m subjective_eval_tools.sum_audio_duration
```

### Batch copy from SoundCloud
For this one you want to git clone the repo and modify soundcloud_auto_gui.py to your needs.  
```bash
uv run python -m subjective_eval_tools.soundcloud_auto_gui --index ./index.json
```
Refer to the docstring at the top of the file.  

## Acknowledgements
Special thanks to [Jingwei Zhao](https://github.com/zhaojw1998) for his pioneering tutorials.  

I welcome feedback! Please open issues.  

## todo
- soundcloud batch copy should use Selenium instead of GUI

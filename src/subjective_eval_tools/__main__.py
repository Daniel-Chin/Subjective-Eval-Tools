from os import path

print('Use one of the modules as entry point instead of the package.')
print()
src_dir = path.dirname(path.abspath(__file__))
with open(path.join(src_dir, 'README.md'), 'r') as f:
    print(f.read())

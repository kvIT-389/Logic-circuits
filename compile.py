import os
import shutil

from PyInstaller.__main__ import run as RunPyInstaller
from colorama import init, Back, Fore

init()
print(Fore.BLACK, Back.YELLOW, end='', sep='')

if input('Continue? [y/n] ') == 'y':
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    name = 'Logic circuits'
    icon = 'icon.ico'
    onefile = False

    if os.path.exists('exe'):
        shutil.rmtree('exe')

    try:
        print(Back.GREEN)
        RunPyInstaller([
            f'--name={name}',
            f'--distpath=exe',
            '--onefile' if onefile else '--onedir',
            '--windowed',
            f'--icon={icon}',
            'main.py'
        ])
    except:
        pass
    else:
        os.remove(f'{name}.spec')
        shutil.rmtree('build')

        additional_files = ['icon.ico']
        for file_ in additional_files:
            shutil.copy(file_, 'exe')

        if not onefile:
            os.chdir('exe')

            for file_ in additional_files:
                shutil.move(file_, name)

            print(Back.YELLOW)
            if input('Do you want to create an archive? [y/n] ') == 'y':
                try:
                    shutil.make_archive(name, 'zip', name)
                except:
                    pass
                else:
                    print(Back.GREEN, 'Archive was created successfully', sep='')
    finally:
        print(Back.CYAN)
        input('<Press Enter to close console>')

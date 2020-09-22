import os
import shutil

from PyInstaller.__main__ import run as RunPyInstaller
from colorama import init, Fore

init()
print(Fore.YELLOW, end='')

if input('Continue? [y/n] ') == 'y':
    name = 'Logic circuits'
    icon = 'icon.ico'
    onefile = False

    if os.path.exists('exe'):
        shutil.rmtree('exe')

    try:
        print(Fore.GREEN)
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

        shutil.copy('icon.ico', 'exe')
        shutil.copytree('png', 'exe/png')

        if not onefile:
            os.chdir('exe')

            shutil.move('icon.ico', name)
            shutil.move('png', name)

            print(Fore.YELLOW)
            if input('Do you want to create an archive? [y/n] ') == 'y':
                try:
                    shutil.make_archive(name, 'zip', name)
                except:
                    pass
                else:
                    print(Fore.GREEN, 'Archive was created successfully', sep='')
    finally:
        print(Fore.CYAN)
        input('<Press Enter to close console>')

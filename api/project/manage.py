#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import shutil
import sys


def manageSettings():
    """ This method will manage settings files for the project. """

    # Check if the configuration key is set
    if 'GENIE_CONFIGURATION_KEY' in os.environ:
        configurationKey = os.environ['GENIE_CONFIGURATION_KEY']
        print(f'\033[41m {configurationKey} \033[0m')
    else:
        configurationKey = 'default'

    # Check if folder exists for the configuration key
    if os.path.isdir(f'project/{configurationKey}'):
        pass
    else:
        os.mkdir(f'project/{configurationKey}')
        print(f'Created {configurationKey} folder')

    if os.path.isfile(f'project/{configurationKey}/settings.py'):
        pass
    else:
        shutil.copyfile('project/base.py',
                        f'project/{configurationKey}/settings.py')
        with open(f'project/{configurationKey}/settings.py', 'r') as file:
            filedata = file.read()
        filedata = filedata.replace('--configuration-key--', configurationKey)
        with open(f'project/{configurationKey}/settings.py', 'w') as file:
            file.write(filedata)

        print(f'Created {configurationKey}.settings.py')

    return f'project.{configurationKey}.settings'


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', manageSettings())
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

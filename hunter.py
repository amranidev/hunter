#!/usr/bin/env python

import os
import sys
from string import Template

hunter_config_dir = os.path.expanduser('~/.hunter')
hunter_config_path = os.path.expanduser('~/.hunter/config')
aws_path = os.path.expanduser('~/.aws/')
template_path = os.getcwd() + '/credentials.template'
config_template_path = os.getcwd() + '/config.template'


def add_new_config_row(credentials_name):
    """
    Add new credentials to the hunter config file.
    @param credentials_name:
    @return:
    """
    path = os.path.expanduser('~/.hunter/config')
    config = credentials_name + ':false'
    file = open(path, 'a')
    file.write(str(config) + "\n")
    file.close()


def update_config_with_used_credentials(credentials_name):
    """
    Update the hunter configuration and use the underlying credentials.
    @param credentials_name:
    @return:
    """
    [hunter_config_file, file_content] = read_hunter_config()

    search = -1
    for credential in file_content:
        search = credential.find(credentials_name)
        if search != -1:
            break

    if search == -1:
        print('Config file does not exists!')
        exit(1)

    results = []
    previous_used = ''
    for credentials in file_content:
        token = credentials.split(':')
        if token[1] == 'true':
            previous_used = token[0]
            token[1] = 'false'

        if token[0] == credentials_name:
            token[1] = 'true'
        results.append(token[0] + ':' + token[1])

    hunter_config_file.close()

    path = os.path.expanduser('~/.hunter/config')
    config_file = open(path, 'w')

    for credentials in results:
        config_file.write(str(credentials) + "\n")
    config_file.close()

    if os.path.exists(aws_path + credentials):
        os.rename(aws_path + 'credentials', aws_path + previous_used)

    if os.path.exists(aws_path + credentials_name):
        os.rename(aws_path + credentials_name, aws_path + 'credentials')
    else:
        print('\033[0;31m' + credentials_name + ' does not exists or the config file is corrupted!')
        exit(1)

    return results


def read_hunter_config():
    """
    Read the underlying hunter config file.
    @return:
    """
    hunter_config_file = open(hunter_config_path, 'r')
    file_content = hunter_config_file.read()
    file_content = file_content.split("\n")
    file_content.remove('')
    return [hunter_config_file, file_content]


def check_if_credentials_exists_before_creating_new_one(credentials_name):
    """
    check if the underlying credential exists.
    @param credentials_name:
    @return:
    """
    if os.path.exists(aws_path + credentials_name):
        print('\033[0;31mERROR: The file is already exists, hunter cannot create this configuration\033[0m')
        exit(1)

    [hunter_config_file, file_content] = read_hunter_config()

    for credentials in file_content:
        token = credentials.split(':')

        if token[0] == credentials_name:
            print('Credentials: ' + credentials_name + ' already in use')
            hunter_config_file.close()
            exit(1)

    hunter_config_file.close()


def new(credentials_name):
    """
    Add new AWS credential.
    @param credentials_name:
    @return:
    """
    check_if_credentials_exists_before_creating_new_one(credentials_name)

    sys.stdout.write('AWS ACCESS KEY: ')
    aws_key = input()
    sys.stdout.write('AWS Secret: ')
    aws_secret = input()
    print('Creating the new credentials ' + credentials_name)

    compiler = {'AWS_KEY': aws_key, 'AWS_SECRET': aws_secret}
    template = open(template_path, 'r')
    content = Template(template.read())

    path = os.path.expanduser('~/.aws/') + credentials_name
    file = open(path, "x")
    file.write(content.substitute(compiler))
    file.close()
    add_new_config_row(credentials_name)
    print('\033[0;32mDone\033[0m')


def use(credentials_name):
    """
    Use the underlying credentials.
    @param credentials_name:
    @return:
    """
    update_config_with_used_credentials(credentials_name)


def delete(credentials_name):
    """
    @param credentials_name:
    """
    if not os.path.exists(aws_path + credentials_name):
        print('\033[0;31m ERROR: Credentials does not exists or already in use.'
              ' Make sure the credentials file exists OR switch the current credentials to a new one.\033[0m')
        exit(1)

    os.remove(aws_path + credentials_name)

    print('\033[0;32mDone\033[0m')


def list_credentials():
    """
    List available credentials.
    """
    [hunter_config_file, file_content] = read_hunter_config()

    for credential in file_content:
        token = credential.split(':')
        used = ''
        if token[1] == "true":
            used = ' *Used as default*'
        print(token[0] + '\033[92m' + used + '\033[0m')

    hunter_config_file.close()


def set_up():
    """
    Setup the AWS and the hunter directories and configurations.
    @return:
    """
    if not os.path.exists(aws_path):
        print('\033[92m Creating .aws directory. \033[0m')
        os.mkdir(aws_path, 755)

    if not os.path.exists(aws_path + 'config'):
        print('\033[92m Creating aws config file: default region: us-east-1 \033[0m')
        template = open(config_template_path, 'r')
        template_content = template.read()
        file = open(aws_path + 'config', 'w')
        file.write(template_content)
        file.close()
        template.close

    if not os.path.exists(hunter_config_dir):
        print('\033[92m Creating .hunter config directory. \033[0m')
        os.mkdir(hunter_config_dir, 755)

    if not os.path.exists(hunter_config_path):
        print('\033[92m Creating hunter config file. \033[0m')
        open(hunter_config_path, 'a').close()


if __name__ == '__main__':

    set_up()
    hunter_commands = ['new', 'delete', 'use', 'list'];

    if len(sys.argv) < 2:
        print('\033[0;31m ERROR: Not enough arguments, run: (man hunter)\033[0m')
        sys.exit(1)

    command = sys.argv[1]

    if command not in hunter_commands:
        print('\033[0;31mERROR:' + command + ' Not found\033[0m')
        sys.exit(1)

    if command == 'list':
        list_credentials()
        # Force exit here because I'm lazy to modify all that shit \_(*<>*)_/
        exit(0)

    try:
        credentials_name = sys.argv[2]
        command_to_execute = globals()[command]
        command_to_execute(credentials_name)
    except IndexError:
        print('\033[0;31m Credential name is not specified\033[0m')

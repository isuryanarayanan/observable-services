# Working with genie.sh, Python, Django

The `genie.sh` shell script is the gateway to start developing with the Genie project. It allows you to start the Docker containers and load the environment variables according to the configuration you want to work in .

## How to use

1. Clone the repository and navigate to the `genie.sh` script:

```bash
$ git clone https://github.com/isuryanarayanan/genie.git
$ cd genie
```

2. Run the script:

```bash
$ ./genie.sh
```

3. Select the configuration you want to work in using the `fzf` prompt. The script will start the Docker containers and load the environment variables.

4. You can now start developing with the Genie project.

## How to add a new configuration

1. Run the `genie.sh` script using the `--create` flag:

```bash
$ ./genie.sh --create
```

2. Give a name and description to the configuration

3. The script will create a new configuration file in the `.genie/configurations` folder.

4. Edit the configuration file according to your needs.

5. Run the `genie.sh` script again and select your new configuration.

## How to build a configuration

1. Run the `genie.sh` script using the `--build` flag:

```bash
$ ./genie.sh --build
```

2. Select the configuration you want to build.

3. The script will build the configuration.

## Additional options

- Use the `-h` or `--help` flag to show the help message and a list of available options.
- Use the `-b` or `--build` flag to build the selected configuration.
- Use the `-c` or `--create` flag to create a new configuration.

For more information, see the [DOCS](https://github.com/isuryanarayanan/genie/docs/) in the repository.

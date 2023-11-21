#!/usr/bin/env bash

# This script is the gateway to start developing with the project.
# It will start the docker containers and load the environment variables according to the
# configuration you want to work in.

# -----------
# How to use:
# -----------
# 1. Run the script
# 2. Select the configuration you want to work in
# 3. The script will start the docker containers and load the environment variables
# 4. You can now start developing

# -----------
# How to add a new configuration:
# -----------
# 1. Run the command using --create flag
# 2. Give a name to the configuration
# 3. Give a description to the configuration
# 4. The script will create a new configuration file in .genie/configurations folder
# 5. Change your configuration file according to your needs
# 6. Run the script and select your new configuration

# -----------
# How to build a configuration:
# -----------
# 1. Run the command using --build flag
# 2. Select the configuration you want to build
# 3. The script will build the configuration
# -----------

# Check if necessary folders are available
if [ ! -d ".genie/configurations" ]; then
    mkdir .genie/configurations
fi

if [ ! -d "conf" ]; then
    mkdir conf
fi


# Flags
create=false
help=false
build=false
up=false
commit=false
workon=false

# Parsing flags
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -c|--create)
    create=true
    shift # past argument
    ;;
    -w|--workon)
    workon=true
    shift # past argument
    ;;
    -u|--up)
    up=true
    shift # past argument
    ;;
    -h|--help)
    help=true
    shift # past argument
    ;;
    -cm|--commit)
    commit=true
    shift # past argument
    ;;
    -b|--build)
    build=true
    shift # past argument
    ;;
    *)    # unknown option
    shift # past argument
    ;;
esac
done

# The workon command is to create a new branch. It will ask for the name of the branch and type of the branch.
# The type of the branch can be the commit flags from the commit_types.json file.
if [ "$workon" = true ]; then
    echo "---------------------"
    echo "Creating a new branch"
    echo "---------------------"

    # Load the JSON file
    data=$(cat .genie/commit_types.json)

    # Convert the JSON data to an array
    IFS=$'\n' read -r -d '' -a options <<< $(echo "$data" | jq -r '.[] | "\(.flag)|\(.version)"')

    # Use fzf to display the options
    selected_option=$(printf '%s\n' "${options[@]}" | fzf --preview='jq -r ".[] | select(.flag==\"$(echo {} | cut -d "|" -f 1)\" and .version==\"$(echo {} | cut -d "|" -f 2)\").description" .genie/commit_types.json')

    # Split the selected option into flag and version
    flag=$(echo $selected_option | cut -d "|" -f 1)
    version=$(echo $selected_option | cut -d "|" -f 2)

    # Print the selected flag and version
    echo "Selected flag: $flag"
    echo "Selected version: $version"

    # Ask for the commit message
    read -p "Enter branch name: " branch_name
    branch="$flag/$branch_name"

    # Convert branch name to small case and replace spaces with dashes
    branch=$(echo $branch | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

    # Show a preview of the commit message and ask if to continue or discard, the text should have a red background
    echo -e "\e[41mBranch name: $branch\e[0m"
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        exit 1
    fi

    echo "---------------------"
    echo "Creating branch..."
    echo "---------------------"
    git checkout -b "$branch"

    exit
fi


# If the commit flag is set, commit the changes
if [ "$commit" = true ]; then
    echo "---------------------"
    echo "Committing changes..."
    echo "---------------------"

    # Load the JSON file
    data=$(cat .genie/commit_types.json)

    # Convert the JSON data to an array
    IFS=$'\n' read -r -d '' -a options <<< $(echo "$data" | jq -r '.[] | "\(.flag)|\(.version)"')

    # Use fzf to display the options
    selected_option=$(printf '%s\n' "${options[@]}" | fzf --preview='jq -r ".[] | select(.flag==\"$(echo {} | cut -d "|" -f 1)\" and .version==\"$(echo {} | cut -d "|" -f 2)\").description" .genie/commit_types.json')

    # Split the selected option into flag and version
    flag=$(echo $selected_option | cut -d "|" -f 1)
    version=$(echo $selected_option | cut -d "|" -f 2)

    # Print the selected flag and version
    echo "Selected flag: $flag"
    echo "Selected version: $version"

    # Ask for the commit message
    read -p "Enter commit message: " message

    # Show a preview of the commit message and ask if to continue or discard, the text should have a red background
    echo -e "\e[41mCommit message: $flag: $message\e[0m"
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        exit 1
    fi

    semantic_version=$(cat .genie/VERSION)

    major=$(echo $semantic_version | cut -d "." -f 1)
    minor=$(echo $semantic_version | cut -d "." -f 2)
    patch=$(echo $semantic_version | cut -d "." -f 3)

    if [ "$version" = "major" ]; then
        major=$((major+1))
        minor=0
        patch=0
    elif [ "$version" = "minor" ]; then
        minor=$((minor+1))
        patch=0
    elif [ "$version" = "patch" ]; then
        patch=$((patch+1))
    fi

    semantic_version="$major.$minor.$patch"
    echo $semantic_version > .genie/VERSION

    git add .
    git commit -m "$flag($version): $message"
    git tag -a $semantic_version -m "$flag($version): $message"
    git push origin
    git push origin $semantic_version

    echo -e "\e[42mChanges committed, new version: $semantic_version\e[0m"
 
    exit
fi

# If help flag is set, show help
if [ "$help" = true ]; then
    echo "Usage: genie.sh [options]"
    echo "Options:"
    echo "  -c, --create     Create a new configuration"
    echo "  -h, --help       Show this help"
    echo "  -b, --build      Build a configuration"
    echo "  -u, --up         Start the containers"
    echo "  -w, --workon     Create a new branch"
    echo "  -cm, --commit    Commit and tag code to main"
    exit
fi

# If create flag is set, create a new configuration
if [ "$create" = true ]; then
    echo "----------------------------"
    echo "Creating a new configuration"
    echo "----------------------------"
    read -p "Enter name: " name
    read -p "Enter description: " description
    read -p "Enter keyword: " keyword
    echo "Creating configuration $name ..."
    echo "{
        \"name\": \"$name\",
        \"description\": \"$description\",
        \"keyword\": \"$keyword\",
        \"binded\": false
    }" > .genie/configurations/$keyword.json
    echo "Configuration file created"
    exit
fi


# Checking FZF installation
if [ $(dpkg-query -W -f='${Status}' fzf 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
	# Requesting root

	SUDO=''
	if (( $EUID != 0 )); then
			echo "Please run as root"
			SUDO='sudo'
			exit
	fi
	$SUDO apt-get install fzf;
fi

# Checking jq installation
if [ $(dpkg-query -W -f='${Status}' jq 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    # Requesting root

    SUDO=''
    if (( $EUID != 0 )); then
            echo "Please run as root"
            SUDO='sudo'
            exit
    fi
    $SUDO apt-get install jq;
fi


# For each mode inside .genie/configurations folder, fzf will show a list of options which is the name of the mode.
# Fzf will also show the mode description as preview.
selected_mode=$(ls .genie/configurations | fzf --prompt "Search configuration > " --preview "cat .genie/configurations/{} | jq '.description'")

# If no mode is selected, exit
if [ -z "$selected_mode" ]; then
    echo "No configuration selected"
    exit
fi

# Load the configuration file
configuration=$(cat .genie/configurations/$selected_mode)

# Check if the configuration is binded
binded=$(echo $configuration | jq '.binded')
# Get the keyword of the configuration
keyword=$(echo $configuration | jq '.keyword')
# Remove quotes from the keyword
keyword=$(echo $keyword | sed 's/"//g')



if [ "$binded" = false ]; then

    # Binding a configuration means the necessary files for container defenition will be created using the base files
    # and the configuration file will be updated to binded=true

    echo "Binding configuration $selected_mode ..."
    
    # If not created create a folder with the name keyword inside the conf folder
    if [ ! -d "conf/$keyword" ]; then
        mkdir conf/$keyword
    fi

    # Copy the base files to the keyword folder
    cp .genie/docker/docker-compose.yml conf/$keyword/docker-compose.yml
    cp .genie/docker/Dockerfile conf/$keyword/Dockerfile
    cp .genie/docker/.env conf/$keyword/.env

    echo "# This is the keyword of the configuration" >> conf/$keyword/.env
    echo "GENIE_CONFIGURATION_KEY=$keyword" >> conf/$keyword/.env

    # Update the docker-compose file to switch the __keyword__ with the keyword
    echo $configuration | jq '.keyword' | sed 's/"//g' | xargs -I {} sed -i "s/__keyword__/{}/g" conf/$keyword/docker-compose.yml

    # Deployment files.
    # Check if environments folder exists
    if [ ! -d "environments" ]; then
        mkdir environments
    fi

    # Check if the keyword folder exists inside environments
    if [ ! -d "environments/$keyword" ]; then
        mkdir environments/$keyword
    fi

    # Copy all the files inside the .genie/environments/ folder to the environments/keyword folder
    cp -r .genie/environments/* environments/$keyword

    # Update the configuration file to binded=true
    echo $configuration | jq '.binded = true' > .genie/configurations/$selected_mode
    echo "Configuration $selected_mode binded"
fi



# Run the docker-compose file
# Only build if the build flag is set
if [ "$build" = true ]; then
    docker compose -f conf/$keyword/docker-compose.yml build

    # Remove all dangling images
    docker image prune -f
    exit
fi

# If the up flag is passed then just run the containers, if not then open a bash session
if [ "$up" = true ]; then
    docker compose -f conf/$keyword/docker-compose.yml up
    read -p "Do you want to close your sessions? [y/n] " close_sessions

    if [ "$close_sessions" != "y" ]; then
        echo "Succesfully exited without closing your session."
        exit
    fi

    docker compose -f conf/$keyword/docker-compose.yml down
    exit
else
    echo "Opening bash session ..."
    docker compose -f conf/$keyword/docker-compose.yml run --service-ports 'project-'$keyword bash
fi


# Ask if the user wants to close the session
read -p "Do you want to close your session? [y/n] " close_session

if [ "$close_session" != "y" ]; then
    echo "Succesfully exited without closing your session."
    exit
fi

docker compose -f conf/$keyword/docker-compose.yml down
echo "Succesfully closed your session."

# docker compose -f conf/local/docker-compose.yml run --service-ports 'project-local' bash
# docker compose -f conf/local/docker-compose.yml run --service-ports 'redis' bash
# docker compose -f conf/local/docker-compose.yml run --service-ports 'celery' bash
#!/usr/bin/env sh

# Change the working directory to be the root of the repository
cd "$(dirname "$0")"

# Install Meteor
curl https://install.meteor.com/ | sh

# Create and activate a Python 2.7 virtual environment
virtualenv --python=python2.7 venv
. venv/bin/activate

# Install the required Python packages
pip install --requirement requirements.txt


#!/usr/bin/env zsh

setopt ERR_EXIT
setopt NO_UNSET

if [[ $# -gt 1 ]]; then
    cat <<-'EOF'
		Usage:

		    $ hat_controller.zsh [SERVER]

		If SERVER is not given, hat.meteor.com is used.
	EOF
    exit 1
fi


# Reload the Arduino's drivers
sudo modprobe --remove cdc_acm
sudo modprobe cdc_acm

server=${1:-hat.meteor.com}
device=$(ls -1 /dev/ttyACM0 | head -n 1)

# Launch hat controller
cd -- ${0:h}/..
unsetopt NO_UNSET
source venv/bin/activate
setopt NO_UNSET
python hat_controller.py -s $server $device


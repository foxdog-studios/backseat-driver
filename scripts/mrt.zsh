#!/usr/bin/env zsh

setopt err_exit
setopt no_unset

repo=$(realpath -- ${0:h}/..)

cd $repo/src
exec mrt $@


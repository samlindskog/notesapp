#!/bin/bash

scriptdir=$(dirname $(readlink -f $0))

function usage () {
	echo "Usage:"
	echo "installenv (install)"
	echo "installenv -u (uninstall)"
	echo "installenv -e (enable wgifctl.service)"
	echo "installenv -h (help)"

	[[ -z $1 ]] && exit 0
	exit $1
}

eflag="no"
uflag="no"
while getopts ":euh" name; do
	case $name in
		e)
			eflag="yes"
			;;
		u)
			uflag="yes"
			;;
		h)
			usage
			;;
		*)
			usage 1
			;;
	esac
done
shift $((OPTIND - 1))

#! /bin/bash
# license: GPLv3
# Copyright 2018, Arne Köhn <arne@chark.eu>

# First, obtain the versions of all plugins (and the main dialogos)
# being used.  Adapt if new plugins are added.

set -e

# needed for compatibility across Linux and MacOS
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

cd $SCRIPTPATH

# make sure the dialogos distribution tree is up to date
cd ..
./gradlew installDist
cd $SCRIPTPATH

# grep all version numbers from build.gradle
dialogosver=$(grep " name:'dialogos'" ../build.gradle | sed "s/.*version:'\(.*\)'/\1/")
sqlitever=$(grep " name:'dialogos-plugin-sqlite'" ../build.gradle | sed "s/.*version:'\(.*\)'/\1/")
nxtver=$(grep " name:'dialogos-plugin-nxt'" ../build.gradle | sed "s/.*version:'\(.*\)'/\1/")

currver=$(git describe)

downloadbase=https://github.com/dialogos/dialogos-distribution/releases/download/$currver/

opts="-D dialogos.core.mavenversion=$dialogosver,dialogos.sqlite.mavenversion=$sqlitever,dialogos.nxt.mavenversion=$nxtver,dialogos.pocketsphinx.mavenversion=$pocketsphinxver,installer.download.base='$downloadbase' dialogos.install4j"

if which install4jc > /dev/null; then
	install4jc $opts
else
	echo "install4j not found in path.  Please run "
	echo install4jc $opts
fi

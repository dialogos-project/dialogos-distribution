#! /bin/bash

# First, obtain the versions of all plugins (and the main dialogos)
# being used.  Adapt if new plugins are added.

dialogosver=$(grep " name:'dialogos'" ../build.gradle | sed "s/.*version:'\(.*\)'/\1/")
sqlitever=$(grep " name:'dialogos-plugin-sqlite'" ../build.gradle | sed "s/.*version:'\(.*\)'/\1/")
nxtver=$(grep " name:'dialogos-plugin-nxt'" ../build.gradle | sed "s/.*version:'\(.*\)'/\1/")
pocketsphinxver=$(grep " name:'dialogos-plugin-pocketsphinx'" ../build.gradle | sed "s/.*version:'\(.*\)'/\1/")

opts="-D dialogos.core.mavenversion=$dialogosver,dialogos.sqlite.mavenversion=$sqlitever,dialogos.nxt.mavenversion=$nxtver,dialogos.pocketsphinx.mavenversion=$pocketsphinxver dialogos.install4j"

if which install4jc > /dev/null; then
	install4jc $opts
else
	echo "install4j not found in path.  Please run "
	echo install4jc $opts
fi

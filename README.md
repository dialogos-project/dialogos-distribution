# DialogOS distribution.

This repository ties together the core of DialogOS with various plugins that should be distributed
by containing all the relevant dependencies in its `build.gradle`, as well as all required data files
(e.g. models for speech recognition). 
It serves two purposes:

 1. We build the installer files from a `full' installation that includes all plugins and data files.
    This works by building and locally installing all files that DialogOS needs to run 
    with all plugins that are deemed useful for distribution. 
    We then call install4j (proprietary software) to make the installer files.
    We finally upload the installer to some webspace.
 2. It can be used to quickly run an installation of DialogOS with all plugins available by calling
    `./gradlew installDist` followed by `build/install/bin/dialogos-distribution`.

For the actual source distribution and documentation please refer to <http://github.com/coli-saar/dialogos>.

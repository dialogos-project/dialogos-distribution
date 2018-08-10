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
     * `./gradlew installDist` followed by `build/install/bin/dialogos-distribution`,
     * or alternatively: `./gradlew run`. 

For the actual source distribution and documentation please refer to 
<http://github.com/dialogos-project/dialogos>.

## Building downloadable installers:

Please refer to the instructions in [`install4j/README`](../blob/master/install4j/README). 
You will need a local installation of [install4j](https://www.ej-technologies.com/products/install4j/overview.html).

## Release process:

For new major/minor versions:

 * make a new branch in the DialogOS repository, call this branch vX.X-release 
 * update the revision of DialogOS both in its `Diamant/src/main/java/com/clt/diamant/Version.java` as well as in `build.gradle`
 * set `IS_NONRELEASE = false;` in `Diamant/src/main/java/com/clt/diamant/Version.java`
 * Test.
 * tag the release commit in dialogos as vX.X.X
 * for all external plugins that you intend to include in the release: have them build against the tagged release of dialogos in `build.gradle`. Test.
 * tag each plugin OR note down the release commit id
 * refer to the updated tags/commit ids in `build.gradle` in dialogos-distribution
 * Test dialogos-distribution, consider updating the CHANGELOG
 * tag the release commit in dialogos-distribution with the exact same tag as you did for dialogos.
 * re-build again, and create installers as per instructions in [`install4j/README`](../blob/master/install4j/README)
 * in dialogos's github.com page, [create a release](https://github.com/dialogos-project/dialogos/releases), associate it with the tag and upload the release.

For bugfix releases:

 * apply any bugfixes necessary to external plugins and create new tag or note down commit id to be released
 * apply bugfixes to the release branch (e.g. by cherry-picking from master)
 * update `Diamant/src/main/java/com/clt/diamant/Version.java`
 * Test.
 * tag bugfix release vX.X.Y ; ALSO do this bugfixes were only applied to plugins and dialogos itself was unchanged. This is important to keep release versions of dialogos-distribution and dialogos in synchrony.
 * continue as above. 


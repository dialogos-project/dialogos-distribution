# DialogOS distribution

**Please report problems with the dialogos-distribution project on the [DialogOS issue tracker](https://github.com/dialogos-project/dialogos/issues)**

This repository ties together the core of DialogOS with various plugins that should be distributed
by containing all the relevant dependencies in its `build.gradle`, as well as all required data files
(e.g. models for speech recognition). 

Its main use is to generate downloadable installers for end users.


## Release process for new major/minor versions

In the code examples below, we create a release for version 2.0.1. Modify the version as needed.

### Create new release of DialogOS Core

On the `master` branch, edit `CHANGELOG.md` to describe the new version. Commit and push your changes.

Create a branch for the new release in the DialogOS (not DialogOS-distribution!) repository:

```
git checkout -b v2.0.1-release
```

Edit `Diamant/src/main/java/com/clt/diamant/Version.java` and `build.gradle` to set the new version. Set `IS_NONRELEASE = false;` in `Diamant/src/main/java/com/clt/diamant/Version.java`.

Test, then push that branch to Github:

```
git commit -am "release 2.0.1"
git push --set-upstream origin v2.0.1-release
```

Tag the release commit in the DialogOS repository:

```
git tag -a v2.0.1 -m "release version v2.0.1"
git push origin --tags
```

### Update SNAPSHOT revision on DialogOS master branch

Revert your working copy of DialogOS to the master branch:

```
git checkout master
```

Edit `Diamant/src/main/java/com/clt/diamant/Version.java` and `build.gradle` to set the new SNAPSHOT version. Ensure that `IS_NONRELEASE` is `true` (as it should always be on the `master` branch). Set the version in `Version.java` to `2.0.2` and in `build.gradle` to `2.0.2-SNAPSHOT`.

Push the snapshot version to Github:

```
git commit -am "set next snapshot release in master branch"
git push
```

### Update plugins

For all plugins that you intend to include in the distribution for your new release (in particular, the NXT and Sqlite plugins): Change their `build.gradle` to point to the tagged release of your new DialogOS version. Rebuild and test.

Update the version of the plugin in `build.gradle` and in the `getVersion` method of the plugin's Plugin subclass. Update the CHANGELOG.md. Rebuild, commit, and push.

Tag the Git version as above and push the tag to Github. This should create a Jitpack artifact for the new version of the plugin.


### Build installers

You will need a local installation of [install4j](https://www.ej-technologies.com/products/install4j/overview.html).

Check out the repository `dialogos-project/dialogos-distribution`.

Set the version in `build.gradle` and in `install4j/dialogos.install4j` (install4j -> application -> version) to the same version of the DialogOS Core.

Edit `build.gradle` so it depends on your new versions of DialogOS Core and the plugins.

Commit and push your changes. Tag the commit with the exact same tag that you used for DialogOS.

Switch to the `install4j` directory and execute `execute-install4j.sh`. This should produce installers with the new version number in the `generated_installers` subdirectory for Windows, Linux, and MacOS.


### Create the release

On the [Github Releases](https://github.com/dialogos-project/dialogos/releases) page for DialogOS (not dialogos-release), select the new tag for your release and click on "Edit Tag". This will bring you to a page that allows you to create a release for that tag. Name the release "DialogOS 2.0.1", add a text that describes the main changes, and upload the full installers that install4j created.


### Update the website

In the `dialogos-project.github.io` repository, modify the tag and release in `_config.yml` to the new version.

## For bugfix releases

 * apply any bugfixes necessary to external plugins and create new tag or note down commit id to be released
 * apply bugfixes to the release branch (e.g. by cherry-picking from master)
 * update `Diamant/src/main/java/com/clt/diamant/Version.java`
 * Test.
 * tag bugfix release vX.X.Y ; ALSO do this if bugfixes were only applied to plugins and dialogos itself was unchanged. This is important to keep release versions of dialogos-distribution and dialogos in synchrony.
 * continue as above. 

Note that new files stemming from new / changed dependencies need to
be added manually to the dialogos.install4j file.  There is no magic
way to recognize them and especially not to group them into the
correct installation bundle.


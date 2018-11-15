import os
import re
import shutil
import subprocess
import sys
import tempfile



### UTILITY METHODS FOR FILE EDITING

def edit_file(filename, replacement_fn):
    tmphandle, tmppath = tempfile.mkstemp(text=True)
    tmpfile = os.fdopen(tmphandle, "w")

    with open(filename, "r") as infile:
        for line in infile:
            replaced = replacement_fn(line)
            if replaced is not None:
                print(replaced, file=tmpfile)
            else:
                print(line.rstrip(), file=tmpfile)

    tmpfile.flush()
    tmpfile.close()

    # overwrite original with edited file
    shutil.copy(filename, f"{filename}.bak")
    shutil.copy(tmppath, filename)

def replace_version_java(v1, v2, v3, is_release):
    # Edits the following lines in Diamant/src/main/java/com/clt/diamant/Version.java:
    #     public static final int MAJOR_VERSION = 2;
    #     public static final int MINOR_VERSION = 0;
    #     public static final int BUGFIX_VERSION = 2;
    #     public static final boolean IS_NONRELEASE = true;

    def replacement_fn(line):
        line = line.rstrip()

        m = re.match(r"(.*MAJOR_VERSION\s*=\s*)(\d+)(.*)", line)
        if m:
            return(f"{m.group(1)}{v1}{m.group(3)}")

        m = re.match(r"(.*MINOR_VERSION\s*=\s*)(\d+)(.*)", line)
        if m:
            return (f"{m.group(1)}{v2}{m.group(3)}")

        m = re.match(r"(.*BUGFIX_VERSION\s*=\s*)(\d+)(.*)", line)
        if m:
            return (f"{m.group(1)}{v3}{m.group(3)}")

        m = re.match(r"(.*IS_NONRELEASE\s*=\s*)([^; \t]+)(.*)", line)
        if m:
            b = "false" if is_release else "true"
            return (f"{m.group(1)}{b}{m.group(3)}")

        return None

    return replacement_fn


def replace_version_plugin_java(v1, v2, v3, is_release):
    # Edits the following lines in Plugin.java of a plugin:
    #     public String getVersion() { return "1.0"; }   // DO NOT EDIT - This line is updated automatically by the make-release script.

    def replacement_fn(line):
        line = line.rstrip()

        m = re.match(r"(.*getVersion.*return \")([^\"]+)(.*)", line)
        if m:
            return(f"{m.group(1)}{v1}.{v2}.{v3}{m.group(3)}")

        return None

    return replacement_fn


def replace_version_plugin_build_gradle(v1, v2, v3, is_release):
    # Edits the following lines in build.gradle OF A PLUGIN:
    #   implementation(group:'com.github.dialogos-project', name:'dialogos', version:'v2.0.1') {
    #   runtime group:'com.github.dialogos-project', name:'dialogos', version:'v2.0.1'
    # def version = '2.0.1'

    # Also applies to buildfile of dialogos-distribution.

    def replacement_fn(line):
        line = line.rstrip()

        # dependencies
        m = re.match(r"(.*name:\s*'dialogos'.*version:')([^']+)(.*)", line)
        if m:
            return f"{m.group(1)}{v1}.{v2}.{v3}{m.group(3)}"

        # my own version
        m = re.match(r"(.*def version = ')([^']+)(.*)", line)
        if m:
            vstring = f"{v1}.{v2}.{v3}"
            if not is_release:
                vstring += "-SNAPSHOT"

            return (f"{m.group(1)}{vstring}{m.group(3)}")


        return None

    return replacement_fn


def replace_version_build_gradle(v1, v2, v3, is_release):
    # Edits the following line in build.gradle OF DIALOGOS-CORE:
    # def version = '2.0.2-SNAPSHOT' // DO NOT EDIT - THIS IS CHANGED BY THE RELEASE SCRIPT
    #   version = '2.0.2-SNAPSHOT'  // DO NOT EDIT - THIS IS CHANGED BY THE RELEASE SCRIPT

    def replacement_fn(line):
        line = line.rstrip()

        m = re.match(r"(.*version = ')([^']+)(.*DO NOT EDIT.*)", line)
        if m:
            vstring = f"{v1}.{v2}.{v3}"
            if not is_release:
                vstring += "-SNAPSHOT"

            return (f"{m.group(1)}{vstring}{m.group(3)}")

        return None

    return replacement_fn


def replace_version_install4j(v1,v2,v3):
    #   <application name="DialogOS" distributionSourceDir="" applicationId="0985-7768-2548-4677" mediaDir="./generated_installers" mediaFilePattern="${compiler:sys.shortName}_${compiler:sys.platform}_${compiler:sys.version}" compression="9" lzmaCompression="true" pack200Compression="true" excludeSignedFromPacking="true" commonExternalFiles="true" createMd5Sums="true" shrinkRuntime="true" shortName="DialogOS" publisher="" publisherWeb="http://dialogos-project.github.io" version="2.0.1" allPathsRelative="true" backupOnSave="false" autoSave="false" convertDotsToUnderscores="true" macSignature="????" macVolumeId="623654d76cd9c023" javaMinVersion="1.7" javaMaxVersion="" allowBetaVM="false" jdkMode="runtimeJre" jdkName="">

    def replacement_fn(line):
        m = re.match(r"(.*application.*DialogOS.*version=\")([^\"]+)(.*)", line)
        if m:
            return f"{m.group(1)}{v1}.{v2}.{v3}{m.group(3)}"

        return None

    return replacement_fn



## Constants

github_base = "https://github.com/dialogos-project"





## Obtain release version

# s_new_version = input("Enter version for the release: ")
s_new_version = "2.0.2"

m = re.match(r"\s*(\d+)\.(\d+)\.(\d+)\s*", s_new_version)
if m:
    v1 = int(m.group(1))
    v2 = int(m.group(2))
    v3 = int(m.group(3))

else:
    m = re.match(r"\s*(\d+)\.(\d+)\s*", s_new_version)
    if m:
        v1 = int(m.group(1))
        v2 = int(m.group(2))
        v3 = 0

vs = f"{v1}.{v2}.{v3}"

## Confirm changelog

# changelog_done = input(f"Have you updated CHANGELOG.md for version {vs} [yes/no]: ")
# if changelog_done.lower().strip() != "yes":
#     print("Please update CHANGELOG.md (you can do this on Github directly) and then rerun the release script.")
#     sys.exit(0)





### CREATE RELEASE FOR DIALOGOS CORE

## Check out repositories
subprocess.run(["git", "clone", f"{github_base}/dialogos"])


## Create branch for release in dialogos
os.chdir("dialogos")
subprocess.run(["git", "checkout", "-b", f"v{vs}-release"])


## Edit dialogos version files
edit_file("Diamant/src/main/java/com/clt/diamant/Version.java", replace_version_java(v1, v2, v3, True))
edit_file("build.gradle", replace_version_build_gradle(v1, v2, v3, True))


## Check that it still builds
cpl = subprocess.run(["./gradlew", "compileJava", "test"])
if cpl.returncode > 0:
    print("\n\nFailed rebuilding dialogos after edits. Please fix and rerun this script.")
    sys.exit(1)

## Publish dialogos-core and all subprojects to maven-local repository so plugins can pick them up
cpl = subprocess.run(["./gradlew", "publishToMavenLocal"])
if cpl.returncode > 0:
    print("\n\nFailed publishing dialogos to Maven Local. Please fix and rerun this script.")
    sys.exit(1)


## Push new versions of these files to Github
# subprocess.run(["git", "commit", "-am", f"release {vs}"])
# subprocess.run(["git", "push", "--set-upstream", "origin", "v{vs}-release"])

## Tag dialogos release; NB tag also defines version name on Jitpack
# subprocess.run(["git", "tag", "-a", f"{vs}", "-m", "release version v{vs}"])
# subprocess.run(["git", "push", "origin", "--tags"])

## Back to original directory
os.chdir("..")





## CREATE RELEASE FOR NXT PLUGIN

# Check out repositories
subprocess.run(["git", "clone", f"{github_base}/dialogos-plugin-nxt"])

# Create branch for release in dialogos
os.chdir("dialogos-plugin-nxt")
subprocess.run(["git", "checkout", "-b", f"v{vs}-release"])

# Edit dialogos version files
edit_file("src/main/java/com/clt/dialogos/lego/nxt/Plugin.java", replace_version_plugin_java(v1, v2, v3, True))
edit_file("build.gradle", replace_version_plugin_build_gradle(v1, v2, v3, True))

# Check that it still builds
cpl = subprocess.run(["./gradlew", "compileJava", "test"])
if cpl.returncode > 0:
    print("\n\nFailed rebuilding NXT plugin after edits. Please fix and rerun this script.")
    sys.exit(1)

# Push new versions of these files to Github
# subprocess.run(["git", "commit", "-am", f"release {vs}: now depends on dialogos-core v{vs}"])
# subprocess.run(["git", "push", "--set-upstream", "origin", "v{vs}-release"])

# Tag dialogos release; NB tag also defines version name on Jitpack
# subprocess.run(["git", "tag", "-a", f"{vs}", "-m", "release version v{vs}"])
# subprocess.run(["git", "push", "origin", "--tags"])

# Back to original directory
os.chdir("..")





## CREATE RELEASE FOR SQLITE PLUGIN

# Check out repositories
subprocess.run(["git", "clone", f"{github_base}/dialogos-plugin-sqlite"])

# Create branch for release in dialogos
os.chdir("dialogos-plugin-sqlite")
subprocess.run(["git", "checkout", "-b", f"v{vs}-release"])

# Edit dialogos version files
edit_file("src/main/java/edu/cmu/lti/dialogos/db/sqlite/Plugin.java", replace_version_plugin_java(v1, v2, v3, True))
edit_file("build.gradle", replace_version_plugin_build_gradle(v1, v2, v3, True))

# Check that it still builds
cpl = subprocess.run(["./gradlew", "compileJava", "test"])
if cpl.returncode > 0:
    print("\n\nFailed rebuilding SQLite plugin after edits. Please fix and rerun this script.")
    sys.exit(1)

# Push new versions of these files to Github
# subprocess.run(["git", "commit", "-am", f"release {vs}: now depends on dialogos-core v{vs}"])
# subprocess.run(["git", "push", "--set-upstream", "origin", "v{vs}-release"])

# Tag dialogos release; NB tag also defines version name on Jitpack
# subprocess.run(["git", "tag", "-a", f"{vs}", "-m", "release version v{vs}"])
# subprocess.run(["git", "push", "origin", "--tags"])

# Back to original directory
os.chdir("..")






## BUILD DISTRIBUTION

# Check out repositories
subprocess.run(["git", "clone", f"{github_base}/dialogos-distribution"])

# Create branch for release in dialogos
os.chdir("dialogos-distribution")
subprocess.run(["git", "checkout", "-b", f"v{vs}-release"])

# Edit version in files
edit_file("install4j/dialogos.install4j", replace_version_install4j(v1, v2, v3))
edit_file("build.gradle", replace_version_plugin_build_gradle(v1, v2, v3, True))





# Push new versions of these files to Github
# subprocess.run(["git", "commit", "-am", f"release {vs}: now depends on dialogos-core v{vs}"])
# subprocess.run(["git", "push", "--set-upstream", "origin", "v{vs}-release"])

# Tag dialogos release; NB tag also defines version name on Jitpack
# subprocess.run(["git", "tag", "-a", f"{vs}", "-m", "release version v{vs}"])
# subprocess.run(["git", "push", "origin", "--tags"])

# Back to original directory
os.chdir("..")

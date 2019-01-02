import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

### PARSING COMMAND-LINE OPTIONS

import argparse
parser = argparse.ArgumentParser(description="Build a DialogOS release.")

parser.add_argument("--publish", action="store_true", default=False, help="Push changes to Github and update the website. Without this option, only local changes are made.")
parser.add_argument("--only-publish", action="store_true", default=False, help="Push changes to Github and update the website. Assumes that the distribution was already built correctly locally and only needs to be pushed.")

args = parser.parse_args()


timestr = "{:%Y_%m_%d_%H:%M:%S}".format(datetime.now())
logfilename = f"log_{timestr}.txt"
absolute_logfilename = os.path.abspath(logfilename)




### UTILITY METHODS FOR FILE EDITING

def check_special_errors(logfile):
    logfile.flush()

    with open(absolute_logfilename, "r") as read_logfile:
        for line in read_logfile:
            if "install4j not found in path" in line:
                print("\nERROR: install4j not found in PATH.")
                print("Please put install4j on the PATH and rerun the script.")
                sys.exit(1)

            m = re.match(r"fatal: destination path '([^']+)' already exists and is not an empty directory.*", line)
            if m:
                print(f"\nERROR: Trying to git clone, but directory '{m.group(1)}' already exists.")
                print("Go to a fresh directory and rerun the script.")
                sys.exit(1)
    

def run(cmdlist, logfile):
    cpl = subprocess.run(cmdlist, stdout=logfile, stderr=logfile)

    if cpl.returncode > 0:
        print(f"\nError while executing command (return code: {cpl.returncode}).")
        print(f"Erroneous command was: {' '.join(cmdlist)}")
        print(f"   in directory {os.getcwd()}")

        check_special_errors(logfile)

        print("Please check the logfile for errors.")
        sys.exit(1)


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
        m = re.match(r"(.*name:\s*'dialogos.*version:')([^']+)(.*)", line)
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
        line = line.rstrip()

        m = re.match(r"(.*application.*DialogOS.*version=\")([^\"]+)(.*)", line)
        if m:
            return f"{m.group(1)}{v1}.{v2}.{v3}{m.group(3)}"

        return None

    return replacement_fn


def replace_version_website(v1,v2,v3):
    # release:
    # tag: v2.0.1
    # version: "2_0_1"

    def replacement_fn(line):
        line = line.rstrip()

        m = re.match(r"(.*tag:\s*)(\S+)(.*)", line)
        if m:
            return f"{m.group(1)}{v1}.{v2}.{v3}{m.group(3)}"

        m = re.match(r"(.*version:\s*\")([^\"]+)(.*)", line)
        if m:
            return f"{m.group(1)}{v1}_{v2}_{v3}{m.group(3)}"

        return None

    return replacement_fn



## Constants

github_base = "https://github.com/dialogos-project"




## GET SOME DATA FROM USER


# ask for version of this release

def parse_version(version_string):
    m = re.match(r"\s*(\d+)\.(\d+)\.(\d+).*", version_string)
    if m:
        v1 = int(m.group(1))
        v2 = int(m.group(2))
        v3 = int(m.group(3))
        return v1, v2, v3

    else:
        m = re.match(r"\s*(\d+)\.(\d+).*", version_string)
        if m:
            v1 = int(m.group(1))
            v2 = int(m.group(2))
            v3 = 0
            return v1, v2, v3

    print("Invalid version string. Please try again.")
    sys.exit(1)


s_new_version = input("Enter version for the release: ")
# s_new_version = "2.0.2"
v1, v2, v3 = parse_version(s_new_version)

vs = f"{v1}.{v2}.{v3}"

# Confirm changelog
changelog_done = input(f"Have you updated CHANGELOG.md for version {vs} [yes/no]: ")
if changelog_done.lower().strip() != "yes":
    print("Please update CHANGELOG.md (you can do this on Github directly) and then rerun the release script.")
    sys.exit(0)


# ask for next development version
dev_proposal_version = f"{v1}.{v2}.{v3+1}-SNAPSHOT"

s_new_dev_version = input(f"Enter version for the next development cycle [default {dev_proposal_version}]: ").strip()
if not s_new_dev_version:
    s_new_dev_version = dev_proposal_version

dv1, dv2, dv3 = parse_version(s_new_dev_version)





## LET'S GO

print(f"\nLogfile is {logfilename}.\n")

with open(logfilename, "w") as logfile:
    if args.only_publish:
        print("Running with option --only-publish, skipping rebuild.")

    else:
        ### CREATE RELEASE FOR DIALOGOS CORE

        print("Updating and building DialogOS Core ...")

        ## Check out repositories
        run(["git", "clone", f"{github_base}/dialogos"], logfile)


        ## Create branch for release in dialogos
        os.chdir("dialogos")
        run(["git", "checkout", "-b", f"v{vs}-release"], logfile)


        ## Edit dialogos version files
        edit_file("Diamant/src/main/java/com/clt/diamant/Version.java", replace_version_java(v1, v2, v3, True))
        edit_file("build.gradle", replace_version_build_gradle(v1, v2, v3, True))
        run(["git", "commit", "-am", f"release {vs}"], logfile)

        ## Check that it still builds
        cpl = subprocess.run(["./gradlew", "compileJava", "test"], stdout=logfile, stderr=logfile)
        if cpl.returncode > 0:
            print("\n\nFailed rebuilding dialogos after edits. Please fix and rerun this script.")
            sys.exit(1)

        ## Publish dialogos-core and all subprojects to maven-local repository so plugins can pick them up
        cpl = subprocess.run(["./gradlew", "publishToMavenLocal"], stdout=logfile, stderr=logfile)
        if cpl.returncode > 0:
            print("\n\nFailed publishing dialogos to Maven Local. Please fix and rerun this script.")
            sys.exit(1)


        ## Back to original directory
        os.chdir("..")





        ## CREATE RELEASE FOR NXT PLUGIN

        print("Updating and building NXT plugin ...")

        # Check out repositories
        run(["git", "clone", f"{github_base}/dialogos-plugin-nxt"], logfile)

        # Create branch for release in dialogos
        os.chdir("dialogos-plugin-nxt")
        run(["git", "checkout", "-b", f"v{vs}-release"], logfile)

        # Edit dialogos version files
        edit_file("src/main/java/com/clt/dialogos/lego/nxt/Plugin.java", replace_version_plugin_java(v1, v2, v3, True))
        edit_file("build.gradle", replace_version_plugin_build_gradle(v1, v2, v3, True))
        run(["git", "commit", "-am", f"release {vs}"], logfile)

        # Check that it still builds
        cpl = subprocess.run(["./gradlew", "compileJava", "test", "publishToMavenLocal"], stdout=logfile, stderr=logfile)
        if cpl.returncode > 0:
            print("\n\nFailed rebuilding NXT plugin after edits. Please fix and rerun this script.")
            sys.exit(1)

        # Back to original directory
        os.chdir("..")





        ## CREATE RELEASE FOR SQLITE PLUGIN

        print("Updating and building SQLite plugin ...")

        # Check out repositories
        run(["git", "clone", f"{github_base}/dialogos-plugin-sqlite"], logfile)

        # Create branch for release in dialogos
        os.chdir("dialogos-plugin-sqlite")
        run(["git", "checkout", "-b", f"v{vs}-release"], logfile)

        # Edit dialogos version files
        edit_file("src/main/java/edu/cmu/lti/dialogos/db/sqlite/Plugin.java", replace_version_plugin_java(v1, v2, v3, True))
        edit_file("build.gradle", replace_version_plugin_build_gradle(v1, v2, v3, True))
        run(["git", "commit", "-am", f"release {vs}"], logfile)

        # Check that it still builds
        cpl = subprocess.run(["./gradlew", "compileJava", "test", "publishToMavenLocal"], stdout=logfile, stderr=logfile)
        if cpl.returncode > 0:
            print("\n\nFailed rebuilding SQLite plugin after edits. Please fix and rerun this script.")
            sys.exit(1)

        # Back to original directory
        os.chdir("..")






        ## BUILD DISTRIBUTION

        print("Updating and building dialogos-distribution ...")

        # Check out repositories
        run(["git", "clone", f"{github_base}/dialogos-distribution"], logfile)

        # Create branch for release in dialogos
        os.chdir("dialogos-distribution")
        run(["git", "checkout", "-b", f"v{vs}-release"], logfile)

        # Edit version in files
        edit_file("install4j/dialogos.install4j", replace_version_install4j(v1, v2, v3))
        edit_file("build.gradle", replace_version_plugin_build_gradle(v1, v2, v3, True))
        run(["git", "commit", "-am", f"release {vs}"], logfile)

        # Build installer
        cpl = subprocess.run(["./gradlew", "build"], stdout=logfile, stderr=logfile)
        if cpl.returncode > 0:
            print("\n\nFailed rebuilding dialogos-distribution after edits. Please fix and rerun this script.")
            sys.exit(1)

        print("Building installers ...")

        os.chdir("install4j")
        cpl = subprocess.run(["./execute-install4j.sh", "build"], stdout=logfile, stderr=logfile)
        if cpl.returncode > 0:
            check_special_errors(logfile)
            print("\n\nFailed building install4j installer. Please fix and rerun this script.")
            sys.exit(1)

        # If install4j fails because install4jc is not in the PATH, add it to the PATH before running
        # the make-release script.
        #
        # On MacOS: export PATH=$PATH:/Applications/install4j.app/Contents/Resources/app/bin

        # Back to original directory
        os.chdir("../..")


        print("Done, installers are in dialogos-distribution/install4j/generated_installers.")
        print(f"Please upload them to Github under the {vs} release on https://github.com/dialogos-project/dialogos/tags")
        print("")



        

    if not args.publish and not args.only_publish:
        print("Skipping 'git push' operations and website modifications.")
        print("If you want them, rerun this script with the --publish option.")


    else:
        ## PUSH AND TAG ALL REPOSITORIES
        ## NB tag also determines version number on Jitpack
        print("Pushing and tagging DialogOS Core to Github ...")

        for dir in ["dialogos", "dialogos-plugin-nxt", "dialogos-plugin-sqlite", "dialogos-distribution"]:
            print(f"Tagging Git versions and pushing to Github: {dir} ...")
            os.chdir(dir)
            run(["git", "push", "--set-upstream", "origin", f"v{vs}-release"], logfile)
            run(["git", "tag", "-a", f"{vs}", "-m", f"release version v{vs}"], logfile)
            run(["git", "push", "origin", "--tags"], logfile)
            os.chdir("..")


        ## PREPARE DIALOGOS FOR NEXT DEVELOPMENT CYCLE
        print(f"Setting version of DialogOS Core to next development version ({s_new_dev_version}) ...")

        os.chdir("dialogos")
        run(["git", "checkout", "master"], logfile)

        # edit dialogos version files
        edit_file("Diamant/src/main/java/com/clt/diamant/Version.java", replace_version_java(dv1, dv2, dv3, False))
        edit_file("build.gradle", replace_version_build_gradle(dv1, dv2, dv3, False))
        run(["git", "commit", "-am", f"prepared for next development cycle: version {s_new_dev_version}"], logfile)
        run(["git", "push"], logfile)

        # check that it still builds
        cpl = subprocess.run(["./gradlew", "compileJava", "test"], stdout=logfile, stderr=logfile)
        if cpl.returncode > 0:
            print("\n\nFailed rebuilding dialogos after edits. Please fix and rerun this script.")
            sys.exit(1)

        os.chdir("..")



        ## UPDATE WEBSITE
        print("Updating website ...")

        run(["git", "clone", f"{github_base}/dialogos-project.github.io"], logfile)
        os.chdir("dialogos-project.github.io")

        edit_file("_config.yml", replace_version_website(v1,v2,v3))

        run(["git", "commit", "-am", f"updated link to release {vs}"], logfile)
        run(["git", "push"], logfile)
    

    print("Done.")


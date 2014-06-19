gedit-gobuild
=============

GoBuild - Gedit 3 plugin for Go develoment. golang 

GoBuild plugin version 1.2 for GEdit. Plugin attaches to on_save event
in GEdit for Go language files only. It does nothing for other file types.

Runs "go build" but if current filename has "_test.go" in the name 
then runs "go test -c" on current file's directory. Waits for number of seconds 
and then timeouts if process takes way too long, so GEdit would not freeze.

Current build directory is determined based on current open file directory.

 * Plug-in designed for fast development on small to mid size projects.
 * Not designed for large Go projects because compilation will timeout if it 
takes too long.
 * Not designed to run Go unit tests. Only compiles them.

![screen1](gobuildscreen1.png)

Plugin captures go build errors and shows them in the Gedit status bar.
It also jumps to the first error and highlights error line if error is in 
the current file.

![screen2](gobuildscreen2.png)

Shows last successful build.

Known issues 
------------

Has been tested on Ubuntu 13.04 and 13.10.

Ubuntu 13.10 requires small change in the gobuild.plugin.
Line with python should be changed to python3 like below:

Loader=python3

This is because Gedit seems to default on using python 3 instead of 
python 2.7 on newer versions of Linux.

Usage
-----

 * Simply drop files into ~/.local/share/gedit/plugins .
 * If this directory does not exist - create it.
 * Start GEdit
 * Open Edit-Preferences, then Plugins and check "GoBuild after save" plugin.
 
Idea
----

Plugin idea is based on the fact that Go builds are fast for even decent size
projects. Because build is fast plugin can run on every Save and still appear 
responsive.
Go development with this plugin goes into tight iteration of save-edit-save-edit
cycle. 

If you work on Go projects with build times over 5 seconds this plugin should be
modified to use keyboard shortcut (such as 'F5') instead of on_save action.

Ops, I forgot to mention...Go is **awesome**. But you probably already know that.

Version 1.2 changes
-------------------

Increased timeout to 11 seconds to allow long running builds.

Fixes issues in 'go test' execution. 
Changed in version 1.2 to compile tests with -c flag only and do not run them.
Prior versions of this plug-in would also run the tests but if tests run long time then they would timeout.
Version 1.2 compiles tests into pkg.test binary but does not run them.
You can run "go test" or "pkg.test" from bash terminal or by other means, not via this plug-in.

Working with multiple Go environments
-------------------------------------

It is possible to work with multiple Go environments by simply setting GOPATH before you execute gedit.
One way to do it is by adding function listed below to .bash_aliases file. Restart your bash session.

Now you can execute something like 

$ gg dev/myproject

Assuming you have folders dev/myproject/src under your home directory. This simple script will
set GOPATH and start gedit.

    function gg() { 
    export GOPATH=/home/your_username/$@
    echo 'path set'
    printenv | grep GOPATH
    cd /home/your_username/$@/src
    gedit > /dev/null 2>&1 &
    }

Instead of starting gedit via shortcut use "gg" alias from the bash. That way your GOPATH will
be correctly set for go build to run. Note: this is important only if you have a need to set 
GOPATH and you have multiple environments to work on.

devrun - bonus plugin
---------------------

devrun is a bonus plugin that simply runs ./dev bash script in current file directory when you press F5.
Current file directory is a folder of the active tab in the Gedit.

The purpose of this plugin is simple: execute ./dev script. I use it to restart webserver but it
can be used for anything. ./dev script should NOT block and return within few seconds.

There is an example of basic ./dev bash script below. It kills old webserver process, rebuilds it and
restarts.

	#!/bin/bash
	killall -9 transsrv
	go build .
	./transsrv -http=:8080 > log.txt 2>&1 &
	
Make sure to add execute permission to this script with chmod +x dev or similar.

styles - bonus styles for GEdit
-------------------------------

Folder /styles contains bonus GEdit style called Nostalgia inspired by VC6. 
Does anyone remember VC6 (MS Visual C++ 6)? At some point it was my favorite IDE... nostalgia.

Put it into ./local/share/gedit/styles and enable style in Preferences.




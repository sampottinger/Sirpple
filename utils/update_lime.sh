#! /bin/bash

# get script directory
SOURCE="$0"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# cd to proj root
cd $DIR/..
if [ ! -f Sirpple/static/jslibs/limejs/.git ]; then
    git submodule update --init
else
    cd Sirpple/static/jslibs/limejs
    git reset --hard HEAD
    cd ../../..
    git submodule update --rebase
fi

#cd to limejs
cd Sirpple/static/jslibs/limejs
git checkout master

if [ ! -f closure ]; then
    # closure does not exist , so init limejs
    bin/lime.py init
else
    cd closure
    #check for updates to closure
    git reset --hard HEAD
    git svn rebase
    ../bin/lime.py update
fi

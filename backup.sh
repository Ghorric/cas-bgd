#!/bin/bash
#
# WSL2: git remote add backup_wsl2 /mnt/c/Users/Leoric/Dropbox/Backup/cas-bgd/
# Windows: git remote add backup C:/Users/Leoric/Dropbox/Backup/cas-bgd/
#
# Retrieve:
#       git clone C:/Users/Leoric/Dropbox/Backup/cas-bgd/

export CURRENT_OS=$(./cas-bgd-scripts/shell/get-os.sh)
export REMOTE=`if [ "$CURRENT_OS" == "MinGw" ] ; then echo "backup" ; else echo "backup_wsl2" ; fi`

echo "Backup with Git: git push $REMOTE master"
git status
git push $REMOTE master


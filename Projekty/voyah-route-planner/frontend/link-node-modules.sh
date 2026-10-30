#!/bin/sh
# npm install nahradí symlink skutečnou složkou → přesunout do node_modules.nosync (iCloud ji nesynchronizuje)
cd "$(dirname "$0")"
if [ -d node_modules ] && [ ! -L node_modules ]; then
  rm -rf node_modules.nosync && mv node_modules node_modules.nosync && ln -s node_modules.nosync node_modules
fi

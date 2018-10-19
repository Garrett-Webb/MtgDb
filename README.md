# MtgDb

## Magic: The Gathering API official site
https://magicthegathering.io/

## Install tools (Debian case)
```
sudo apt install curl git
sudo apt install python-3
```

## How to build a simplified single json and zip
```
# build to dist/
python3 src/build.py

# clean
rm -r dist/
```

## How to update
```
# all
python3 src/mtg.py

# individual update
python3 src/mtg.py help
python3 src/mtg.py <task> ...

# diff
git diff

# git commit
git commit -a
```

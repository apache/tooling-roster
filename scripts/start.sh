#!/bin/sh
# What `docker compose up` runs (see compose.yaml): copy the tree in, make a certificate,
# write a development config.yaml with the roles of yours, and start the dev server.

set -eu

if [ -d /tmp/roster ]
then
    echo "This script must be run in a clean container; run docker compose down first!"
    exit 1
fi

# Source is mounted at /mnt
# /run/roster/.venv and /run/roster/assets/node_modules are mounted
# from external volumes so we don't want to overwrite them

# copy locally so changes don't affect host
rm -rf /tmp/roster
cp -Rp /mnt /tmp/roster

# don't want host versions of these
rm -rf /tmp/roster/state
rm -rf /tmp/roster/.venv
rm -rf /tmp/roster/assets/.yarn/install-state.gz
rm -rf /tmp/roster/assets/node_modules
rm -rf /tmp/roster/.git
rm -rf /tmp/roster/.github
rm -rf /tmp/roster/app/client/static/assets

# move what's left across, avoiding any overwrites
cd /tmp/roster
find . -type d -exec mkdir -p /run/roster/{} \;
find . -type f -exec mv -n {} /run/roster/{} \;

cd /run/roster

# replace app copies with links (generated files were dropped above)
find app -type f -exec ln -sf /mnt/{} /run/roster/{} \;

# Get cert data from cache if possible
if [ -r /run/cert/cert.pem ] && [ -r /run/cert/key.pem ]
then
    echo "Found existing cert pair"
    mkdir -p state
    cp /run/cert/*.pem state
else
    echo "Creating a new cert pair"
    make certs # create the certs
    # Safety first: we don't need the key any more
    rm "$(mkcert -CAROOT)/rootCA-key.pem"

    # cache for next time
    cp state/*.pem /run/cert
    cp "$(mkcert -CAROOT)/rootCA.pem" /run/cert

    # make it easy to fetch the cert if needed
    cp "$(mkcert -CAROOT)/rootCA.pem" state
fi

cp config.yaml.example config.yaml
sed -i 's|host: localhost|host: 0.0.0.0|' config.yaml

make sync
make init
# The frontend's dependencies, which the watcher `make dev` starts imports. The bundle `make build`
# also writes is thrown away when the watcher starts; it is the same command the devcontainer runs.
make build

# The roles of the config.yaml CONTRIBUTING.md has you write, and nothing else of it: the rest of a file
# written for the host - its port, a mail server, its paths - does not fit the container.
if [ -f /mnt/config.yaml ]; then
    uv run python - <<'PYTHON'
import pathlib

import yaml

mine = yaml.safe_load(pathlib.Path("/mnt/config.yaml").read_text()) or {}
if "roles" in mine:
    path = pathlib.Path("config.yaml")
    config = yaml.safe_load(path.read_text()) or {}
    config["roles"] = mine["roles"]
    path.write_text(yaml.safe_dump(config, sort_keys=False))
    print("config.yaml: the roles from your config.yaml")
PYTHON
fi

make dev

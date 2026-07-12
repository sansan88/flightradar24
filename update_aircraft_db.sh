#!/bin/bash
# Update the local SkyAware aircraft database from the FlightAware dump1090 repository.
# Runs at boot via update_aircraft_db.service (as root).
set -u

REPO_DIR="/home/flightradar/dump1090"
DB_TARGET="/usr/share/skyaware/html/db"

# git pull as the owning user, so the checkout doesn't end up root-owned
if runuser -u flightradar -- git -C "$REPO_DIR" pull --ff-only; then
    echo "git pull OK"
else
    echo "git pull failed (no network?), copying existing checkout anyway"
fi

cp -r "$REPO_DIR/public_html/db/." "$DB_TARGET/"
echo "aircraft database updated in $DB_TARGET"

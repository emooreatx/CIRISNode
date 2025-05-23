#!/bin/bash
# CIRISNode server setup script
# Usage: sudo bash setup_ciris_users.sh

set -e

# Create 'ciris' user for running services
if ! id "ciris" &>/dev/null; then
    adduser --disabled-password --gecos "CIRIS Service User" ciris
    echo "Created user 'ciris'"
else
    echo "User 'ciris' already exists"
fi

# Add 'ciris' to docker group
usermod -aG docker ciris

echo "Added 'ciris' to docker group."

# Do NOT add 'ciris' to sudoers

# Create 'chunky' user and add to sudoers
if ! id "chunky" &>/dev/null; then
    adduser --disabled-password --gecos "Chunky Sudo User" chunky
    echo "Created user 'chunky'"
else
    echo "User 'chunky' already exists"
fi

usermod -aG sudo chunky

echo "Added 'chunky' to sudo group."

echo "All done!"

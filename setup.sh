#!/usr/bin/env bash
set -euo pipefail

echo "RUNNING SETUP"

# Define the packages we need on each distro
PKG_CFG_PKGS=""
FONTCONFIG_PKGS=""

if command -v apt-get &>/dev/null; then
  PM_UPDATE="sudo apt-get update"
  PM_INSTALL="sudo apt-get install -y"
  PKG_CFG_PKGS="pkg-config"
  FONTCONFIG_PKGS="libfontconfig1-dev"

elif command -v pacman &>/dev/null; then
  PM_UPDATE="sudo pacman -Sy"
  PM_INSTALL="sudo pacman -S --noconfirm"
  PKG_CFG_PKGS="pkgconf"
  FONTCONFIG_PKGS="fontconfig"

elif command -v dnf &>/dev/null; then
  PM_UPDATE="sudo dnf makecache"
  PM_INSTALL="sudo dnf install -y"
  PKG_CFG_PKGS="pkgconf-pkg-config"
  FONTCONFIG_PKGS="fontconfig-devel"

elif command -v yum &>/dev/null; then
  PM_UPDATE="sudo yum makecache"
  PM_INSTALL="sudo yum install -y"
  PKG_CFG_PKGS="pkgconfig"
  FONTCONFIG_PKGS="fontconfig-devel"

elif command -v zypper &>/dev/null; then
  PM_UPDATE="sudo zypper refresh"
  PM_INSTALL="sudo zypper install -y"
  PKG_CFG_PKGS="pkg-config"
  FONTCONFIG_PKGS="fontconfig-devel"

elif command -v brew &>/dev/null; then
  PM_UPDATE="brew update"
  PM_INSTALL="brew install"
  PKG_CFG_PKGS="pkg-config"
  FONTCONFIG_PKGS="fontconfig"

else
  echo "⚠️  No supported package manager found. Please install pkg-config and fontconfig dev libraries manually."
  PM_UPDATE=""
  PM_INSTALL=""
fi

# Install system dependencies if we have a package manager
if [[ -n "$PM_INSTALL" ]]; then
  echo "[Installing system dependencies: $PKG_CFG_PKGS & $FONTCONFIG_PKGS]"
  $PM_UPDATE
  $PM_INSTALL $PKG_CFG_PKGS $FONTCONFIG_PKGS
fi

# Create Python virtualenv if it doesn’t exist
VENV_DIR="env"
if [ ! -d "$VENV_DIR" ]; then
  echo "[Creating Python virtual environment in ./$VENV_DIR]"
  python3 -m venv "$VENV_DIR"
fi

# Activate and install Python requirements
echo "[Activating virtualenv]"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "[Upgrading pip and installing Python requirements]"
pip install --upgrade pip
pip install -r requirements.txt

# Build/develop Rust extension
echo "[Building Rust core library with maturin]"
maturin develop --release

echo "Setup complete!"

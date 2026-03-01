#!/bin/sh
# DocPlatform installer — https://valoryx.org
# Usage: curl -fsSL https://valoryx.org/install.sh | sh
set -e

REPO="Valoryx-org/releases"
BINARY="docplatform"

# ---------- detect OS ----------
OS="$(uname -s)"
case "$OS" in
  Linux*)  OS="linux"  ;;
  Darwin*) OS="darwin" ;;
  *)
    echo "Error: Unsupported operating system: $OS" >&2
    echo "DocPlatform supports Linux and macOS. For Windows, download the .exe from:" >&2
    echo "  https://github.com/$REPO/releases/latest" >&2
    exit 1
    ;;
esac

# ---------- detect architecture ----------
ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64)   ARCH="amd64" ;;
  aarch64|arm64)   ARCH="arm64" ;;
  *)
    echo "Error: Unsupported architecture: $ARCH" >&2
    exit 1
    ;;
esac

URL="https://github.com/$REPO/releases/latest/download/${BINARY}-${OS}-${ARCH}"
INSTALL_DIR="/usr/local/bin"

echo "Downloading $BINARY for $OS/$ARCH..."
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TMPDIR/$BINARY"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TMPDIR/$BINARY" "$URL"
else
  echo "Error: curl or wget is required" >&2
  exit 1
fi

chmod +x "$TMPDIR/$BINARY"

# ---------- install ----------
if [ -w "$INSTALL_DIR" ]; then
  mv "$TMPDIR/$BINARY" "$INSTALL_DIR/$BINARY"
else
  echo "Installing to $INSTALL_DIR (requires sudo)..."
  sudo mv "$TMPDIR/$BINARY" "$INSTALL_DIR/$BINARY"
fi

echo "Installed $BINARY to $INSTALL_DIR/$BINARY"
"$INSTALL_DIR/$BINARY" version 2>/dev/null || true
echo ""
echo "Get started:"
echo "  $BINARY init --workspace-name \"My Docs\" --slug my-docs"
echo "  $BINARY serve"

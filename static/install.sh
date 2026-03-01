#!/bin/sh
# DocPlatform installer — https://valoryx.org
# Usage: curl -fsSL https://valoryx.org/install.sh | sh
#        curl -fsSL https://valoryx.org/install.sh | sh -s -- --version v0.5.0
set -e

REPO="Valoryx-org/releases"
BINARY="docplatform"
VERSION=""
INSTALL_DIR="/usr/local/bin"

# ---------- parse flags ----------
while [ $# -gt 0 ]; do
  case "$1" in
    --version|-v)  VERSION="$2"; shift 2 ;;
    --dir|-d)      INSTALL_DIR="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: curl -fsSL https://valoryx.org/install.sh | sh -s -- [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --version, -v VERSION   Install a specific version (e.g. v0.5.0)"
      echo "  --dir, -d DIR           Install to DIR instead of /usr/local/bin"
      echo "  --help, -h              Show this help"
      exit 0
      ;;
    *)  echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# ---------- detect OS ----------
RAW_OS="$(uname -s)"
case "$RAW_OS" in
  Linux*)  OS="linux"  ;;
  Darwin*) OS="darwin" ;;
  MINGW*|MSYS*|CYGWIN*)
    echo "Error: This installer is for Linux and macOS." >&2
    echo "On Windows, download the .exe directly:" >&2
    echo "  https://github.com/$REPO/releases/latest" >&2
    exit 1
    ;;
  *)
    echo "Error: Unsupported operating system: $RAW_OS" >&2
    exit 1
    ;;
esac

# ---------- detect architecture ----------
RAW_ARCH="$(uname -m)"
case "$RAW_ARCH" in
  x86_64|amd64)    ARCH="amd64" ;;
  aarch64|arm64)   ARCH="arm64" ;;
  armv7l)
    echo "Error: 32-bit ARM is not supported. DocPlatform requires arm64." >&2
    exit 1
    ;;
  *)
    echo "Error: Unsupported architecture: $RAW_ARCH" >&2
    exit 1
    ;;
esac

# ---------- build download URL ----------
FILENAME="${BINARY}-${OS}-${ARCH}"
if [ -n "$VERSION" ]; then
  BASE_URL="https://github.com/$REPO/releases/download/$VERSION"
else
  BASE_URL="https://github.com/$REPO/releases/latest/download"
fi

BINARY_URL="$BASE_URL/$FILENAME"
CHECKSUMS_URL="$BASE_URL/checksums.txt"

# ---------- choose downloader ----------
download() {
  local url="$1" dest="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 3 --retry-delay 2 "$url" -o "$dest"
  elif command -v wget >/dev/null 2>&1; then
    wget -q --tries=3 -O "$dest" "$url"
  else
    echo "Error: curl or wget is required." >&2
    exit 1
  fi
}

# ---------- download ----------
echo "Downloading $BINARY for $OS/$ARCH..."
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

if ! download "$BINARY_URL" "$TMPDIR/$BINARY"; then
  echo "" >&2
  echo "Error: Download failed." >&2
  if [ -n "$VERSION" ]; then
    echo "Check that version '$VERSION' exists at:" >&2
  else
    echo "Check that a release exists at:" >&2
  fi
  echo "  https://github.com/$REPO/releases" >&2
  exit 1
fi

# ---------- verify checksum ----------
if command -v sha256sum >/dev/null 2>&1; then
  HASH_CMD="sha256sum"
elif command -v shasum >/dev/null 2>&1; then
  HASH_CMD="shasum -a 256"
else
  HASH_CMD=""
fi

if [ -n "$HASH_CMD" ]; then
  if download "$CHECKSUMS_URL" "$TMPDIR/checksums.txt" 2>/dev/null; then
    EXPECTED=$(grep "  $FILENAME\$" "$TMPDIR/checksums.txt" | awk '{print $1}')
    if [ -n "$EXPECTED" ]; then
      ACTUAL=$($HASH_CMD "$TMPDIR/$BINARY" | awk '{print $1}')
      if [ "$EXPECTED" != "$ACTUAL" ]; then
        echo "Error: Checksum verification failed!" >&2
        echo "  Expected: $EXPECTED" >&2
        echo "  Got:      $ACTUAL" >&2
        echo "The download may be corrupted. Please try again." >&2
        exit 1
      fi
      echo "Checksum verified."
    fi
  fi
fi

chmod +x "$TMPDIR/$BINARY"

# ---------- verify binary runs ----------
if ! "$TMPDIR/$BINARY" version >/dev/null 2>&1; then
  echo "Warning: Binary downloaded but could not execute 'version' command." >&2
  echo "This may indicate an incompatible platform." >&2
fi

# ---------- install ----------
if [ -w "$INSTALL_DIR" ]; then
  mv "$TMPDIR/$BINARY" "$INSTALL_DIR/$BINARY"
elif command -v sudo >/dev/null 2>&1; then
  echo "Installing to $INSTALL_DIR (requires sudo)..."
  sudo mv "$TMPDIR/$BINARY" "$INSTALL_DIR/$BINARY"
else
  echo "Error: $INSTALL_DIR is not writable and sudo is not available." >&2
  echo "Run with --dir to install elsewhere:" >&2
  echo "  curl -fsSL https://valoryx.org/install.sh | sh -s -- --dir ~/.local/bin" >&2
  exit 1
fi

INSTALLED_VERSION=$("$INSTALL_DIR/$BINARY" version 2>/dev/null || echo "unknown")
echo ""
echo "Installed $BINARY to $INSTALL_DIR/$BINARY"
echo "  $INSTALLED_VERSION"
echo ""
echo "Get started:"
echo "  $BINARY init --workspace-name \"My Docs\" --slug my-docs"
echo "  $BINARY serve"

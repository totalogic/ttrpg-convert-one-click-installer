#!/usr/bin/env bash
set -eu

CLI_REPOSITORY="ebullient/ttrpg-convert-cli"
DATA_REPOSITORY="5etools-mirror-3/5etools-src"
VERSION="latest"
SETUP_SRD="false"
NON_INTERACTIVE="false"
DRY_RUN="false"
DATA_DIR=""
SRD_OUTPUT=""
INSTALL_ROOT="${TTRPG_INSTALL_ROOT:-$HOME/.local/share/ttrpg-convert-cli}"
BIN_DIR="${TTRPG_BIN_DIR:-$HOME/.local/bin}"
DATA_CACHE_ROOT="${TTRPG_DATA_CACHE:-$HOME/.local/share/ttrpg-convert-data}"
CONFIG_DIR="${TTRPG_CONFIG_DIR:-$HOME/.config/ttrpg-convert}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

usage() {
    printf '%s\n' \
        "Usage: install.sh [options]" \
        "  --with-srd             Generate the optional D&D 2024/5.5e SRD collection" \
        "  --srd-output PATH      SRD Markdown output directory" \
        "  --data-dir PATH        Existing 5etools source directory" \
        "  --version VERSION      Install a specific release (default: latest)" \
        "  --non-interactive      Do not prompt for optional SRD setup" \
        "  --dry-run              Print the installation plan without changing anything" \
        "  -h, --help             Show this help"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --with-srd) SETUP_SRD="true" ;;
        --srd-output) shift; SRD_OUTPUT=${1:?Missing path for --srd-output} ;;
        --data-dir) shift; DATA_DIR=${1:?Missing path for --data-dir} ;;
        --version) shift; VERSION=${1:?Missing value for --version} ;;
        --non-interactive) NON_INTERACTIVE="true" ;;
        --dry-run) DRY_RUN="true" ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

step() {
    printf '==> %s\n' "$1"
}

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        printf 'Required command not found: %s\n' "$1" >&2
        exit 1
    fi
}

case "$(uname -s)" in
    Linux)
        case "$(uname -m)" in
            x86_64|amd64) ASSET_PLATFORM="linux-x86_64" ;;
            *) printf 'Unsupported Linux architecture: %s\n' "$(uname -m)" >&2; exit 1 ;;
        esac
        PROFILE_FILES="$HOME/.profile"
        ;;
    Darwin)
        case "$(uname -m)" in
            arm64|aarch64) ASSET_PLATFORM="osx-aarch_64" ;;
            x86_64|amd64) ASSET_PLATFORM="osx-x86_64" ;;
            *) printf 'Unsupported macOS architecture: %s\n' "$(uname -m)" >&2; exit 1 ;;
        esac
        PROFILE_FILES="$HOME/.profile $HOME/.zprofile"
        ;;
    *)
        printf 'This installer supports macOS and Linux. On Windows, use install.cmd.\n' >&2
        exit 1
        ;;
esac

if [ "$DRY_RUN" = "true" ]; then
    printf 'DRY_RUN=true\nASSET=%s\nINSTALL_ROOT=%s\nSETUP_SRD=%s\n' \
        "$ASSET_PLATFORM" "$INSTALL_ROOT" "$SETUP_SRD"
    exit 0
fi

require_command curl
require_command unzip

TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/ttrpg-convert-installer.XXXXXX")
cleanup() {
    rm -rf "$TMP_ROOT"
}
trap cleanup EXIT INT TERM

if [ "$VERSION" = "latest" ]; then
    RELEASE_URL=$(curl -fsSL -o /dev/null -w '%{url_effective}' "https://github.com/$CLI_REPOSITORY/releases/latest")
    VERSION=${RELEASE_URL##*/}
fi

ARCHIVE_NAME="ttrpg-convert-cli-$VERSION-$ASSET_PLATFORM.zip"
CHECKSUM_NAME="$ARCHIVE_NAME.sha256"
DOWNLOAD_BASE="https://github.com/$CLI_REPOSITORY/releases/download/$VERSION"
ARCHIVE_PATH="$TMP_ROOT/$ARCHIVE_NAME"
CHECKSUM_PATH="$TMP_ROOT/$CHECKSUM_NAME"

step "Downloading TTRPG Convert $VERSION"
curl -fL --retry 3 -o "$ARCHIVE_PATH" "$DOWNLOAD_BASE/$ARCHIVE_NAME"
curl -fL --retry 3 -o "$CHECKSUM_PATH" "$DOWNLOAD_BASE/$CHECKSUM_NAME"
EXPECTED_HASH=$(tr -d '[:space:]' < "$CHECKSUM_PATH")
if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL_HASH=$(sha256sum "$ARCHIVE_PATH")
    ACTUAL_HASH=${ACTUAL_HASH%% *}
elif command -v shasum >/dev/null 2>&1; then
    ACTUAL_HASH=$(shasum -a 256 "$ARCHIVE_PATH")
    ACTUAL_HASH=${ACTUAL_HASH%% *}
else
    printf 'Neither sha256sum nor shasum is available.\n' >&2
    exit 1
fi
if [ "$EXPECTED_HASH" != "$ACTUAL_HASH" ]; then
    printf 'SHA-256 mismatch. Expected %s but got %s.\n' "$EXPECTED_HASH" "$ACTUAL_HASH" >&2
    exit 1
fi
step "Checksum verified"

EXTRACT_DIR="$TMP_ROOT/cli"
mkdir -p "$EXTRACT_DIR"
unzip -q "$ARCHIVE_PATH" -d "$EXTRACT_DIR"
SOURCE_EXECUTABLE=$(find "$EXTRACT_DIR" -type f -name 'ttrpg-convert' -print -quit)
if [ -z "$SOURCE_EXECUTABLE" ]; then
    printf 'The release archive did not contain ttrpg-convert.\n' >&2
    exit 1
fi

VERSION_DIR="$INSTALL_ROOT/versions/$VERSION"
mkdir -p "$VERSION_DIR" "$BIN_DIR"
cp "$SOURCE_EXECUTABLE" "$VERSION_DIR/ttrpg-convert"
chmod 755 "$VERSION_DIR/ttrpg-convert"
ln -sfn "$VERSION_DIR/ttrpg-convert" "$BIN_DIR/ttrpg-convert"

PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
for profile in $PROFILE_FILES; do
    if [ ! -f "$profile" ] || ! grep -F "$PATH_LINE" "$profile" >/dev/null 2>&1; then
        printf '\n%s\n' "$PATH_LINE" >> "$profile"
    fi
done
export PATH="$BIN_DIR:$PATH"

step "Verifying installation"
"$BIN_DIR/ttrpg-convert" --version

if [ "$SETUP_SRD" != "true" ] && [ "$NON_INTERACTIVE" != "true" ] && [ -t 0 ]; then
    printf 'Set up the optional D&D 2024/5.5e SRD Markdown collection now? [y/N] '
    read -r answer
    case "$answer" in
        y|Y|yes|YES) SETUP_SRD="true" ;;
    esac
fi

write_embedded_config() {
    destination=$1
    mkdir -p "$(dirname "$destination")"
    cat > "$destination" <<'JSON'
{
  "sources": {
    "reference": ["srd52", "basicRules2024"]
  },
  "reprintBehavior": "newest",
  "images": {
    "copyInternal": false,
    "copyExternal": false
  },
  "tagPrefix": "ttrpg-cli"
}
JSON
}

find_tools_root() {
    root=$1
    if [ -d "$root/data" ]; then
        printf '%s\n' "$root"
        return
    fi
    candidate=$(find "$root" -type d -name data -print -quit)
    if [ -z "$candidate" ]; then
        return 1
    fi
    dirname "$candidate"
}

if [ "$SETUP_SRD" = "true" ]; then
    step "Preparing D&D 2024/5.5e SRD conversion"
    if [ -n "$DATA_DIR" ]; then
        if [ ! -d "$DATA_DIR/data" ]; then
            printf 'The --data-dir path must contain a data directory.\n' >&2
            exit 1
        fi
        TOOLS_ROOT=$DATA_DIR
    else
        DATA_RELEASE_URL=$(curl -fsSL -o /dev/null -w '%{url_effective}' "https://github.com/$DATA_REPOSITORY/releases/latest")
        DATA_VERSION=${DATA_RELEASE_URL##*/}
        DATA_ASSET="5etools-$DATA_VERSION.zip"
        DATA_ARCHIVE="$TMP_ROOT/$DATA_ASSET"
        DATA_RELEASE_JSON="$TMP_ROOT/5etools-release.json"
        curl -fsSL -o "$DATA_RELEASE_JSON" "https://api.github.com/repos/$DATA_REPOSITORY/releases/tags/$DATA_VERSION"
        EXPECTED_DATA_HASH=$(awk -v target="$DATA_ASSET" '
            index($0, "\"name\": \"" target "\"") { found=1 }
            found && index($0, "\"digest\": \"sha256:") {
                line=$0
                sub(/^.*sha256:/, "", line)
                sub(/\".*$/, "", line)
                print line
                exit
            }
        ' "$DATA_RELEASE_JSON")
        if [ -z "$EXPECTED_DATA_HASH" ]; then
            printf 'Could not find a SHA-256 digest for %s.\n' "$DATA_ASSET" >&2
            exit 1
        fi
        step "Downloading 5etools data $DATA_VERSION (only open 2024 SRD content will be generated)"
        curl -fL --retry 3 -o "$DATA_ARCHIVE" "https://github.com/$DATA_REPOSITORY/releases/download/$DATA_VERSION/$DATA_ASSET"
        if command -v sha256sum >/dev/null 2>&1; then
            ACTUAL_DATA_HASH=$(sha256sum "$DATA_ARCHIVE")
            ACTUAL_DATA_HASH=${ACTUAL_DATA_HASH%% *}
        else
            ACTUAL_DATA_HASH=$(shasum -a 256 "$DATA_ARCHIVE")
            ACTUAL_DATA_HASH=${ACTUAL_DATA_HASH%% *}
        fi
        if [ "$EXPECTED_DATA_HASH" != "$ACTUAL_DATA_HASH" ]; then
            printf '5etools data SHA-256 mismatch.\n' >&2
            exit 1
        fi
        DATA_EXTRACT="$DATA_CACHE_ROOT/$DATA_VERSION"
        rm -rf "$DATA_EXTRACT"
        mkdir -p "$DATA_EXTRACT"
        unzip -q "$DATA_ARCHIVE" -d "$DATA_EXTRACT"
        TOOLS_ROOT=$(find_tools_root "$DATA_EXTRACT") || {
            printf 'Could not locate the 5etools data directory after extraction.\n' >&2
            exit 1
        }
    fi

    if [ -z "$SRD_OUTPUT" ]; then
        SRD_OUTPUT="$HOME/Documents/TTRPG-5.5e-SRD"
    fi
    mkdir -p "$SRD_OUTPUT" "$CONFIG_DIR"
    CONFIG_PATH="$CONFIG_DIR/srd-2024.json"
    if [ -f "$SCRIPT_DIR/config/srd-2024.json" ]; then
        cp "$SCRIPT_DIR/config/srd-2024.json" "$CONFIG_PATH"
    else
        write_embedded_config "$CONFIG_PATH"
    fi

    step "Generating Obsidian-ready 2024 SRD Markdown"
    "$BIN_DIR/ttrpg-convert" --index -c "$CONFIG_PATH" -o "$SRD_OUTPUT" "$TOOLS_ROOT"
    printf 'SRD_OUTPUT=%s\n' "$SRD_OUTPUT"
fi

printf '\nTTRPG Convert installed successfully.\n'
printf 'Executable: %s/ttrpg-convert\n' "$BIN_DIR"
printf 'Open a new terminal, then run: ttrpg-convert --help\n'

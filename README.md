# TTRPG Convert One-Click Installer

Cross-platform, no-admin installer for [TTRPG Convert CLI](https://github.com/ebullient/ttrpg-convert-cli), with an optional D&D 2024/“5.5e” SRD-to-Markdown setup for Obsidian.

This repository is an independent convenience installer. It is not affiliated with or endorsed by the TTRPG Convert CLI or 5etools maintainers.

## What it does

- Detects the current stable TTRPG Convert release.
- Selects the correct native binary for Windows, macOS Intel, macOS Apple Silicon, or Linux x86-64.
- Downloads and verifies the release SHA-256 checksum.
- Installs without administrator/root privileges.
- Adds the command to the current user's `PATH`.
- Verifies the installation with `ttrpg-convert --version`.
- Optionally downloads current 5etools source data and generates **only** the open 2024 rules selected by `srd52` and `basicRules2024`.

## One-click installation

### Windows

1. Download this repository as a ZIP and extract it.
2. Double-click **`install.cmd`**.
3. Choose whether to generate the optional 2024/5.5e SRD Markdown collection.

No administrator prompt is required.

### macOS

1. Download this repository as a ZIP and extract it.
2. Double-click **`install.command`**.
3. Choose whether to generate the optional 2024/5.5e SRD Markdown collection.

If macOS blocks the first launch, right-click `install.command`, choose **Open**, and approve it once.

### Linux

Run:

```bash
bash install.sh
```

Depending on the desktop environment, `install.sh` can also be marked executable and launched from the file manager.

## Quick install from GitHub

After reviewing the scripts, the installer can be launched directly from the repository.

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/totalogic/ttrpg-convert-one-click-installer/main/install.ps1 | iex
```

macOS/Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/totalogic/ttrpg-convert-one-click-installer/main/install.sh | bash
```

## Command-line installation

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

Install the CLI and generate the 2024 SRD without prompting:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -SetupSrd -NonInteractive
```

Choose an Obsidian vault subdirectory for the generated Markdown:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -SetupSrd -SrdOutput "C:\Vaults\My Vault\TTRPG-5.5e-SRD" -NonInteractive
```

### macOS or Linux

```bash
bash install.sh
```

Install the CLI and generate the 2024 SRD without prompting:

```bash
bash install.sh --with-srd --non-interactive
```

Choose an Obsidian vault subdirectory:

```bash
bash install.sh --with-srd --srd-output "$HOME/Documents/My Vault/TTRPG-5.5e-SRD" --non-interactive
```

## Existing 5etools data

To avoid downloading the latest 5etools release, point the installer at an existing source directory containing a `data` folder.

Windows:

```powershell
.\install.ps1 -SetupSrd -DataDir "D:\5etools" -NonInteractive
```

macOS/Linux:

```bash
bash install.sh --with-srd --data-dir "$HOME/5etools" --non-interactive
```

## Default locations

| Platform | CLI installation | Command | Default SRD output |
|---|---|---|---|
| Windows | `%LOCALAPPDATA%\Programs\ttrpg-convert-cli` | `ttrpg-convert.exe` | `Documents\TTRPG-5.5e-SRD` |
| macOS/Linux | `~/.local/share/ttrpg-convert-cli` | `~/.local/bin/ttrpg-convert` | `~/Documents/TTRPG-5.5e-SRD` |

The downloaded 5etools archive is cached under the current user's application-data directory so the generated collection can be refreshed later.

## Updating

Run the installer again. It discovers the latest stable release, verifies it, installs the new version, and updates the command entry point.

## Security

- Native CLI archives are checked against the `.sha256` files published with TTRPG Convert releases.
- The optional 5etools archive is checked against the SHA-256 digest published by GitHub's Releases API.
- The installer never requests administrator/root privileges.
- `--dry-run` / `-DryRun` prints the platform and destination without downloading or changing anything.

## Content and licensing note

The optional SRD workflow downloads a 5etools source archive but configures TTRPG Convert to generate only entries tagged as the 2024 SRD 5.2 or 2024 Free Rules. The repository does not bundle TTRPG data.

Respect copyrights and content creators. Configure additional books or other sources only when you own or are otherwise authorized to use them.

TTRPG Convert CLI and downloaded datasets retain their own licenses and terms. See [NOTICE](NOTICE.md).

## Development and tests

```bash
python -m unittest discover -s tests -v
```

Dry runs:

```powershell
.\install.ps1 -DryRun -SetupSrd
```

```bash
bash install.sh --dry-run --with-srd
```

CI exercises unit checks and real CLI installation on Windows, macOS, and Linux.

## License

The installer code in this repository is licensed under the MIT License. See [LICENSE](LICENSE).

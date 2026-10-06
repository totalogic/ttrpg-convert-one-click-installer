# TTRPG Convert One-Click Installer

[![Test installers](https://github.com/totalogic/ttrpg-convert-one-click-installer/actions/workflows/test.yml/badge.svg)](https://github.com/totalogic/ttrpg-convert-one-click-installer/actions/workflows/test.yml)
[![Build graphical installer](https://github.com/totalogic/ttrpg-convert-one-click-installer/actions/workflows/gui-build.yml/badge.svg)](https://github.com/totalogic/ttrpg-convert-one-click-installer/actions/workflows/gui-build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A beginner-friendly, cross-platform installer for [Ebullient’s TTRPG Convert CLI](https://github.com/ebullient/ttrpg-convert-cli), with an optional workflow that creates an Obsidian-ready **D&D 2024 / 5.5e open-rules collection**.

- Windows, macOS, and Linux
- Graphical wizard plus terminal installers
- No administrator or root access
- No Java installation when a native release is available
- SHA-256 verification before installation
- Optional SRD 5.2 and 2024 Free Rules conversion
- Safe staged updates that preserve the previous installation or output if verification fails

> [!IMPORTANT]
> This is an independent convenience installer—not the TTRPG Convert application itself. Ebullient’s upstream project supplies the converter, conversion logic, templates, and official binaries.

## Which repository do I need?

| Repository | Purpose |
|---|---|
| **This repository** | Downloads, verifies, installs, updates, and initially configures TTRPG Convert. |
| **[ebullient/ttrpg-convert-cli](https://github.com/ebullient/ttrpg-convert-cli)** | The actual conversion engine and authoritative upstream project. |

**Ebullient built the engine; this project provides an installation wizard and a ready-made 2024 open-rules preset.**

## What the installer does

1. Detects your operating system and CPU architecture.
2. Finds the requested TTRPG Convert release.
3. Downloads the official upstream native binary.
4. Verifies the binary against its published SHA-256 checksum.
5. Runs the downloaded executable’s version check before making it active.
6. Installs it for the current user and updates the user’s `PATH`.
7. Optionally downloads and verifies 5etools source data.
8. Optionally generates linked Markdown using only `srd52` and `basicRules2024`.
9. Builds generated notes in a staging directory before replacing an existing output.

The installer does not bundle or redistribute upstream binaries or datasets.

## Before you start

### Supported systems

| Platform | Supported architecture |
|---|---|
| Windows 10/11 | 64-bit x86 |
| macOS | Apple Silicon or 64-bit Intel |
| Linux | 64-bit x86 |

### Requirements

- Internet access
- Windows: PowerShell 5.1 or newer
- macOS/Linux: `bash`, `curl`, `unzip`, and either `sha256sum` or `shasum`
- Obsidian is optional; the generated files are ordinary Markdown

**No GitHub login, activation code, administrator prompt, or Java installation is required.**

The packaged graphical app does not require Python. Running the graphical app from source requires Python 3 with Tkinter; the terminal installers do not.

---

# Graphical installer

The graphical wizard is a thin wrapper around the same tested PowerShell and Bash installers used by the terminal flow. It lets you:

- install or update TTRPG Convert for the current user;
- optionally generate the D&D 2024 / 5.5e open-rules collection;
- choose the Obsidian/output folder and an existing 5etools data folder;
- preview the exact installer command without changing the system;
- follow progress and verification output in a built-in log;
- explicitly enable replacement of a non-empty output folder.

Packaged apps for Windows, macOS, and Linux are produced by the **Build graphical installer** workflow. Download the artifact for your operating system, extract it, and run `TTRPG-Convert-Installer`.

To run the GUI from a downloaded source archive instead:

| Platform | Launcher |
|---|---|
| Windows | Double-click `install-gui.cmd` |
| macOS | Double-click `install-gui.command` |
| Linux | Run `./install-gui.sh` |

If Python/Tkinter is unavailable, use the terminal launcher described below. The installer logic, checksum verification, staging, and rollback behavior are the same in both interfaces.

---

# Content Selector

The Content Selector is a graphical interface for choosing which content to pull from ttrpg-convert-cli and where to save it. It lets you:

- browse and select 5eTools books, adventures, and reference sources by name;
- add homebrew JSON files to include in the conversion;
- choose between saving output to a **local directory** or pushing to a **remote git repository**;
- configure conversion options (reprint behavior, races-as-species, split rules, dice roller, images, tag prefix);
- preview the generated config JSON and the exact conversion command before running;
- save the configuration file for reuse or scripting;
- run the conversion with live progress output and cancel support.

## Launching the Content Selector

| Platform | Launcher |
|---|---|
| Windows | Double-click `content-selector.cmd` |
| macOS/Linux | Run `./content-selector.sh` |

From source:

```bash
python content-selector.py
```

The Content Selector requires Python 3 with Tkinter. It does not require the installer to have been run first, but `ttrpg-convert` must be installed (via the installer above or the upstream project) before running a conversion.

## How it works

1. **Select sources** in the Books, Adventures, and Reference tabs. Open-rule sources (`srd52`, `basicRules2024`) are selected by default.
2. **Add homebrew** (optional) by browsing for JSON files.
3. **Choose a save location**: a local directory, or a remote git repository (with branch and optional subdirectory).
4. **Set conversion options**: reprint behavior, races-as-species, split rules, dice roller, tag prefix, and image handling.
5. **Preview** the generated config and command in the Preview & Run tab.
6. **Run** the conversion, or **Save config file** to reuse it with `ttrpg-convert -c config.json`.

For remote repository output, the selector clones the repo, converts into the specified subdirectory, commits, and pushes.

---

# Windows installation

## Terminal fallback: download and double-click

1. Select the green **Code** button on this GitHub page.
2. Select **Download ZIP**.
3. Right-click the downloaded ZIP and select **Extract All**.
4. Open the extracted folder. Do not run the installer from inside the ZIP preview.
5. Double-click:

```text
install.cmd
```

When asked whether to generate the optional 2024/5.5e SRD collection:

- Enter `y` to install the CLI and create the Markdown collection.
- Press **Enter** to install only the CLI.

Close the installer, open a **new** PowerShell or Command Prompt window, and verify:

```powershell
ttrpg-convert --version
```

# macOS installation

For the GUI, use the packaged macOS artifact or double-click `install-gui.command` from the extracted source archive.

For the terminal installer:

1. Select **Code → Download ZIP**.
2. Open the downloaded ZIP and then the extracted folder.
3. Double-click `install.command`.

If macOS blocks it, right-click `install.command`, select **Open**, and confirm. If necessary, open Terminal in the folder and run:

```bash
chmod +x install.command install.sh
./install.command
```

Open a new Terminal window and verify:

```bash
ttrpg-convert --version
```

# Linux installation

For the GUI, use the packaged Linux artifact or run `./install-gui.sh` from the extracted source archive.

For the terminal installer:

1. Download and extract the repository, or clone it.
2. Open a terminal in the repository directory.
3. Run:

```bash
bash install.sh
```

4. Open a new terminal and verify:

```bash
ttrpg-convert --version
```

## Advanced: direct installation commands

These commands execute the current `main` branch directly. Downloading and reviewing the scripts first is safer and is the recommended method.

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/totalogic/ttrpg-convert-one-click-installer/main/install.ps1 | iex
```

macOS/Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/totalogic/ttrpg-convert-one-click-installer/main/install.sh | bash
```

---

# Generate the 2024 / 5.5e open-rules collection

The optional preset selects only:

- `srd52` — SRD 5.2
- `basicRules2024` — 2024 Free Rules

It also enables:

- `racesAsSpecies: true`
- `splitRules: true`
- newest reprints
- no automatic image copying

Default output:

| Platform | Directory |
|---|---|
| Windows | `Documents\TTRPG-5.5e-SRD` |
| macOS/Linux | `~/Documents/TTRPG-5.5e-SRD` |

The preset does **not** automatically enable commercial sourcebooks.

## Generate without prompts

Windows:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -SetupSrd -NonInteractive
```

macOS/Linux:

```bash
bash install.sh --with-srd --non-interactive
```

## Generate inside an Obsidian vault

Windows:

```powershell
.\install.ps1 `
  -SetupSrd `
  -SrdOutput "C:\Vaults\My Vault\TTRPG-5.5e-SRD" `
  -NonInteractive
```

macOS/Linux:

```bash
bash install.sh \
  --with-srd \
  --srd-output "$HOME/Documents/My Vault/TTRPG-5.5e-SRD" \
  --non-interactive
```

## Existing-output safety

The installer refuses to write into a non-empty output directory by default. Conversion happens in a separate staging directory, so failed generation does not damage the existing collection.

To intentionally replace an existing collection **after a successful staged conversion**:

Windows:

```powershell
.\install.ps1 -SetupSrd -SrdOutput "C:\Vaults\My Vault\TTRPG-5.5e-SRD" -Force -NonInteractive
```

macOS/Linux:

```bash
bash install.sh --with-srd --srd-output "$HOME/Documents/My Vault/TTRPG-5.5e-SRD" --force --non-interactive
```

> [!WARNING]
> `-Force` / `--force` removes the previous output only after the replacement has been generated successfully. Keep normal backups of important vaults anyway.

## Use existing 5etools source data

The supplied path must contain a `data` directory.

Windows:

```powershell
.\install.ps1 -SetupSrd -DataDir "D:\5etools" -NonInteractive
```

macOS/Linux:

```bash
bash install.sh --with-srd --data-dir "$HOME/5etools" --non-interactive
```

---

# Command-line options

## Windows PowerShell

| Option | Meaning |
|---|---|
| `-SetupSrd` | Generate the optional 2024 open-rules collection. |
| `-SrdOutput "PATH"` | Select the Markdown output directory. |
| `-DataDir "PATH"` | Use an existing 5etools source directory. |
| `-Version "VERSION"` | Install a particular upstream release. |
| `-NonInteractive` | Disable prompts. |
| `-Force` | Safely replace a non-empty SRD output after successful generation. |
| `-DryRun` | Display the installation plan without changing anything. |

```powershell
.\install.ps1 -DryRun -SetupSrd
```

## macOS/Linux

| Option | Meaning |
|---|---|
| `--with-srd` | Generate the optional 2024 open-rules collection. |
| `--srd-output PATH` | Select the Markdown output directory. |
| `--data-dir PATH` | Use an existing 5etools source directory. |
| `--version VERSION` | Install a particular upstream release. |
| `--non-interactive` | Disable prompts. |
| `--force` | Safely replace a non-empty SRD output after successful generation. |
| `--dry-run` | Display the installation plan without changing anything. |
| `--help` | Show installer help. |

```bash
bash install.sh --dry-run --with-srd
```

---

# Installation locations

| Platform | Versioned installation | Active command | Extracted data cache |
|---|---|---|---|
| Windows | `%LOCALAPPDATA%\Programs\ttrpg-convert-cli\versions` | `%LOCALAPPDATA%\Programs\ttrpg-convert-cli\bin\ttrpg-convert.exe` | `%LOCALAPPDATA%\ttrpg-convert\data` |
| macOS/Linux | `~/.local/share/ttrpg-convert-cli/versions` | `~/.local/bin/ttrpg-convert` | `~/.local/share/ttrpg-convert-data` |

The downloaded archive is temporary. Extracted source data is retained in the data cache.

# Updating

Run the installer again. It verifies the requested release before switching the active command. If the new executable fails its version check, the previous active version remains in place.

Install a specific version with `-Version` on Windows or `--version` on macOS/Linux.

# Uninstalling

Generated Markdown is not removed automatically.

## Windows

1. Remove `%LOCALAPPDATA%\Programs\ttrpg-convert-cli`.
2. Optionally remove `%LOCALAPPDATA%\ttrpg-convert` to clear cached data and configuration.
3. Remove the installer’s `bin` directory from your user `PATH` through **Environment Variables**.

## macOS/Linux

```bash
rm -rf "$HOME/.local/share/ttrpg-convert-cli"
rm -f "$HOME/.local/bin/ttrpg-convert"
rm -rf "$HOME/.local/share/ttrpg-convert-data"
rm -rf "$HOME/.config/ttrpg-convert"
```

Remove the corresponding `export PATH="..."` line from your shell profile if you no longer use that directory for other commands.

---

# Troubleshooting

## `ttrpg-convert` is not recognized or command not found

Close all terminal windows and open a new one. Existing terminals do not automatically reload user `PATH` changes.

Windows direct verification:

```powershell
& "$env:LOCALAPPDATA\Programs\ttrpg-convert-cli\bin\ttrpg-convert.exe" --version
```

macOS/Linux direct verification:

```bash
"$HOME/.local/bin/ttrpg-convert" --version
```

## The Windows window closes before I can read the error

Open PowerShell in the repository directory and run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

## GitHub API rate limit

Wait and retry, or set `GITHUB_TOKEN` to a token that can read public repositories. Never commit or share the token.

## Checksum mismatch

The installer intentionally stops. Do not bypass verification. Check the network or proxy and retry later.

## The output directory is not empty

Choose a new directory, or use `-Force` / `--force` if replacement is intentional. Replacement is staged before the old output is removed.

## SRD generation takes several minutes

That is normal. The workflow downloads source data and creates more than a thousand linked Markdown files.

---

# Security and content notice

- The installer runs entirely at user scope.
- Official TTRPG Convert archives are checked against upstream `.sha256` files.
- Optional source data is checked against the digest published by GitHub’s Releases API.
- New executables are verified before activation.
- Existing generated output is retained until replacement generation succeeds.
- Pull-request CI does not expose a GitHub token to installer code.
- No commercial sourcebooks are selected by the included preset.

Use only content you own or are authorized to use. TTRPG Convert CLI, 5etools data, trademarks, and related content retain their own licenses and terms. See [NOTICE.md](NOTICE.md).

# Where to report a problem

| Problem | Report it to |
|---|---|
| Download, checksum, installation, `PATH`, prompts, or this SRD preset | This repository |
| Incorrect generated Markdown, links, templates, parsing, or unsupported source behavior | [Upstream TTRPG Convert](https://github.com/ebullient/ttrpg-convert-cli/issues) |

# Development

```bash
python -m unittest discover -s tests -v
bash -n install.sh install.command install-gui.sh install-gui.command
python gui/ttrpg_installer_gui.py --self-test
```

CI runs unit checks on pull requests and real installation smoke tests on trusted pushes across Windows, macOS, and Linux. A separate workflow builds a self-tested PyInstaller package natively on all three operating systems and uploads each package as a workflow artifact.

## License

The installer code in this repository is licensed under the [MIT License](LICENSE).

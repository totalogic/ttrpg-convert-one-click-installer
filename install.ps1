[CmdletBinding()]
param(
    [switch]$SetupSrd,
    [string]$SrdOutput = "",
    [string]$DataDir = "",
    [string]$Version = "latest",
    [switch]$NonInteractive,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$CliRepository = "ebullient/ttrpg-convert-cli"
$DataRepository = "5etools-mirror-3/5etools-src"
$AssetPlatform = "windows-x86_64"
$InstallRoot = Join-Path $env:LOCALAPPDATA "Programs\ttrpg-convert-cli"
$BinDirectory = Join-Path $InstallRoot "bin"
$DataCacheRoot = Join-Path $env:LOCALAPPDATA "ttrpg-convert\data"
$ConfigDirectory = Join-Path $env:LOCALAPPDATA "ttrpg-convert\config"

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-Sha256([string]$File, [string]$Expected) {
    $actual = (Get-FileHash -Algorithm SHA256 -Path $File).Hash.ToLowerInvariant()
    $expectedNormalized = $Expected.Trim().ToLowerInvariant()
    if ($actual -ne $expectedNormalized) {
        throw "SHA-256 mismatch for $File. Expected $expectedNormalized but got $actual."
    }
}

function Add-ToUserPath([string]$Directory) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @($userPath -split ";" | Where-Object { $_ })
    $alreadyPresent = $parts | Where-Object {
        $_.TrimEnd("\", "/").Equals($Directory.TrimEnd("\", "/"), [StringComparison]::OrdinalIgnoreCase)
    }
    if (-not $alreadyPresent) {
        $newPath = if ($userPath) { "$Directory;$userPath" } else { $Directory }
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    }
    if (($env:Path -split ";") -notcontains $Directory) {
        $env:Path = "$Directory;$env:Path"
    }
}

function Get-Release([string]$Repository, [string]$RequestedVersion) {
    $endpoint = if ($RequestedVersion -eq "latest") {
        "https://api.github.com/repos/$Repository/releases/latest"
    } else {
        "https://api.github.com/repos/$Repository/releases/tags/$RequestedVersion"
    }
    return Invoke-RestMethod -Headers @{ "User-Agent" = "ttrpg-convert-one-click-installer" } -Uri $endpoint
}

function Get-SrdConfig([string]$Destination) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    $bundled = Join-Path $PSScriptRoot "config\srd-2024.json"
    if ($PSScriptRoot -and (Test-Path $bundled)) {
        Copy-Item -Force $bundled $Destination
        return
    }

    @'
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
'@ | Set-Content -Encoding UTF8 -Path $Destination
}

function Find-ToolsRoot([string]$ExtractedRoot) {
    if (Test-Path (Join-Path $ExtractedRoot "data")) {
        return $ExtractedRoot
    }
    $candidate = Get-ChildItem -Directory -Recurse -Path $ExtractedRoot |
        Where-Object { Test-Path (Join-Path $_.FullName "data") } |
        Select-Object -First 1
    if (-not $candidate) {
        throw "Could not locate the 5etools data directory after extraction."
    }
    return $candidate.FullName
}

if (-not [Environment]::Is64BitOperatingSystem) {
    throw "The Windows installer requires a 64-bit operating system."
}

if ($DryRun) {
    Write-Output "DRY_RUN=true"
    Write-Output "ASSET=$AssetPlatform"
    Write-Output "INSTALL_ROOT=$InstallRoot"
    Write-Output "SETUP_SRD=$($SetupSrd.ToString().ToLowerInvariant())"
    exit 0
}

$tempDirectory = Join-Path ([IO.Path]::GetTempPath()) ("ttrpg-convert-installer-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tempDirectory | Out-Null

try {
    Write-Step "Finding TTRPG Convert release"
    $release = Get-Release $CliRepository $Version
    $releaseVersion = $release.tag_name
    $archiveName = "ttrpg-convert-cli-$releaseVersion-$AssetPlatform.zip"
    $checksumName = "$archiveName.sha256"
    $archiveAsset = $release.assets | Where-Object { $_.name -eq $archiveName } | Select-Object -First 1
    $checksumAsset = $release.assets | Where-Object { $_.name -eq $checksumName } | Select-Object -First 1
    if (-not $archiveAsset -or -not $checksumAsset) {
        throw "Release $releaseVersion does not contain $archiveName and its checksum."
    }

    $archivePath = Join-Path $tempDirectory $archiveName
    $checksumPath = Join-Path $tempDirectory $checksumName
    Write-Step "Downloading TTRPG Convert $releaseVersion"
    Invoke-WebRequest -UseBasicParsing -Uri $archiveAsset.browser_download_url -OutFile $archivePath
    Invoke-WebRequest -UseBasicParsing -Uri $checksumAsset.browser_download_url -OutFile $checksumPath

    $expectedHash = (Get-Content -Raw $checksumPath).Trim().Split()[0]
    Test-Sha256 $archivePath $expectedHash
    Write-Step "Checksum verified"

    $extractPath = Join-Path $tempDirectory "cli"
    Expand-Archive -Force -Path $archivePath -DestinationPath $extractPath
    $sourceExecutable = Get-ChildItem -Recurse -File -Filter "ttrpg-convert.exe" -Path $extractPath | Select-Object -First 1
    if (-not $sourceExecutable) {
        throw "The release archive did not contain ttrpg-convert.exe."
    }

    $versionDirectory = Join-Path (Join-Path $InstallRoot "versions") $releaseVersion
    New-Item -ItemType Directory -Force -Path $versionDirectory, $BinDirectory | Out-Null
    Copy-Item -Force $sourceExecutable.FullName (Join-Path $versionDirectory "ttrpg-convert.exe")
    Copy-Item -Force $sourceExecutable.FullName (Join-Path $BinDirectory "ttrpg-convert.exe")
    Add-ToUserPath $BinDirectory

    $installedExecutable = Join-Path $BinDirectory "ttrpg-convert.exe"
    Write-Step "Verifying installation"
    & $installedExecutable --version
    if ($LASTEXITCODE -ne 0) {
        throw "ttrpg-convert failed its version check."
    }

    $doSrd = $SetupSrd
    if (-not $SetupSrd -and -not $NonInteractive) {
        $answer = Read-Host "Set up the optional D&D 2024/5.5e SRD Markdown collection now? [y/N]"
        $doSrd = $answer -match "^[Yy]"
    }

    if ($doSrd) {
        Write-Step "Preparing D&D 2024/5.5e SRD conversion"
        $toolsRoot = $DataDir
        if ($toolsRoot) {
            $toolsRoot = (Resolve-Path $toolsRoot).Path
            if (-not (Test-Path (Join-Path $toolsRoot "data"))) {
                throw "DataDir must point to a 5etools source directory containing a data folder."
            }
        } else {
            $dataRelease = Get-Release $DataRepository "latest"
            $dataAsset = $dataRelease.assets | Where-Object { $_.name -like "5etools-*.zip" } | Select-Object -First 1
            if (-not $dataAsset -or -not $dataAsset.digest -or -not $dataAsset.digest.StartsWith("sha256:")) {
                throw "The current 5etools release has no downloadable zip with a SHA-256 digest."
            }
            $dataVersion = $dataRelease.tag_name
            $dataArchivePath = Join-Path $tempDirectory $dataAsset.name
            Write-Step "Downloading 5etools data $dataVersion (only open 2024 SRD content will be generated)"
            Invoke-WebRequest -UseBasicParsing -Uri $dataAsset.browser_download_url -OutFile $dataArchivePath
            Test-Sha256 $dataArchivePath $dataAsset.digest.Substring(7)

            $dataExtractPath = Join-Path $DataCacheRoot $dataVersion
            if (Test-Path $dataExtractPath) {
                Remove-Item -Force -Recurse $dataExtractPath
            }
            New-Item -ItemType Directory -Force -Path $dataExtractPath | Out-Null
            Expand-Archive -Force -Path $dataArchivePath -DestinationPath $dataExtractPath
            $toolsRoot = Find-ToolsRoot $dataExtractPath
        }

        if (-not $SrdOutput) {
            $SrdOutput = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "TTRPG-5.5e-SRD"
        }
        New-Item -ItemType Directory -Force -Path $SrdOutput, $ConfigDirectory | Out-Null
        $configPath = Join-Path $ConfigDirectory "srd-2024.json"
        Get-SrdConfig $configPath

        Write-Step "Generating Obsidian-ready 2024 SRD Markdown"
        & $installedExecutable --index -c $configPath -o $SrdOutput $toolsRoot
        if ($LASTEXITCODE -ne 0) {
            throw "SRD conversion failed with exit code $LASTEXITCODE."
        }
        Write-Host "SRD_OUTPUT=$SrdOutput"
    }

    Write-Host ""
    Write-Host "TTRPG Convert installed successfully." -ForegroundColor Green
    Write-Host "Executable: $installedExecutable"
    Write-Host "Open a new terminal, then run: ttrpg-convert --help"
} finally {
    if (Test-Path $tempDirectory) {
        Remove-Item -Force -Recurse $tempDirectory
    }
}

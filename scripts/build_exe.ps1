#Requires -Version 7.4
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$Python = Join-Path $RepoRoot '.venv/Scripts/python.exe'
$BuildRoot = Join-Path $RepoRoot 'build'
$DistRoot = Join-Path $RepoRoot 'dist'

function Invoke-Python {
    param([string[]] $Arguments)
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw 'Virtualenv Python command failed; build stopped.'
    }
}

function Reset-GeneratedDirectory {
    param([string] $Target)
    $Resolved = [IO.Path]::GetFullPath($Target)
    $Allowed = @(
        [IO.Path]::GetFullPath((Join-Path $RepoRoot 'build')),
        [IO.Path]::GetFullPath((Join-Path $RepoRoot 'dist'))
    )
    if ($Resolved -notin $Allowed) {
        throw 'Refusing to clean a path outside the project build/dist directories.'
    }
    if (Test-Path -LiteralPath $Resolved) {
        $Item = Get-Item -LiteralPath $Resolved -Force
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'Refusing to clean a linked build/dist directory.'
        }
        $Links = @(Get-ChildItem -LiteralPath $Resolved -Recurse -Force -Attributes ReparsePoint)
        if ($Links.Count -ne 0) {
            throw 'Refusing to clean build/dist directories containing links.'
        }
        Write-Host "Cleaning generated directory: $Resolved"
        Remove-Item -LiteralPath $Resolved -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Resolved -Force | Out-Null
}

if (-not $IsWindows -or -not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw 'Windows and the project .venv/Scripts/python.exe are required.'
}

Push-Location $RepoRoot
$PreviousTemp = $env:TEMP
$PreviousTmp = $env:TMP
$PreviousPyInstallerConfig = $env:PYINSTALLER_CONFIG_DIR
try {
    # Python 3.14 preserves the venv prefix under -S; inspect before site/.pth loading.
    & $Python -I -S (Join-Path $PSScriptRoot 'build_environment.py')
    if ($LASTEXITCODE -ne 0) {
        throw 'Build environment rejected before cleanup. Follow the clean-venv steps in README.'
    }
    Invoke-Python -Arguments @('-c', 'import struct, sys; assert sys.version_info[:2] == (3, 14); assert struct.calcsize("P") == 8')
    Invoke-Python -Arguments @('-m', 'PyInstaller', '--version')
    # Only generated directories are removed; never source, .git, or .venv.
    Reset-GeneratedDirectory $BuildRoot
    Reset-GeneratedDirectory $DistRoot
    $env:TEMP = Join-Path $BuildRoot 'tmp'
    $env:TMP = $env:TEMP
    $env:PYINSTALLER_CONFIG_DIR = Join-Path $BuildRoot 'pyinstaller-cache'
    New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null

    $Version = & $Python -m scripts.windows_version --print-version
    if ($LASTEXITCODE -ne 0) { throw 'Unable to read source package version.' }
    $Version = $Version.Trim()
    $VersionFile = Join-Path $BuildRoot 'windows-version.txt'
    Invoke-Python -Arguments @('-m', 'scripts.windows_version', '--output', $VersionFile)

    $DataFile = Join-Path $RepoRoot 'src/pwcheck/data/common_passwords.txt'
    $EntryPoint = Join-Path $RepoRoot 'src/pwcheck/__main__.py'
    $Common = @(
        '-m', 'PyInstaller', '--noconfirm', '--clean', '--console', '--noupx',
        '--name', 'pwcheck', '--paths', (Join-Path $RepoRoot 'src'),
        '--hidden-import', 'pwcheck.data', '--add-data', "${DataFile}:pwcheck/data",
        '--version-file', $VersionFile
    )
    $Icon = Join-Path $RepoRoot 'assets/pwcheck.ico'
    if (Test-Path -LiteralPath $Icon -PathType Leaf) {
        $Common += @('--icon', $Icon)
    }

    Invoke-Python -Arguments ($Common + @(
        '--onefile', '--distpath', $DistRoot,
        '--workpath', (Join-Path $BuildRoot 'onefile'),
        '--specpath', (Join-Path $BuildRoot 'specs/onefile'), $EntryPoint
    ))
    Invoke-Python -Arguments ($Common + @(
        '--onedir', '--distpath', (Join-Path $DistRoot 'folder'),
        '--workpath', (Join-Path $BuildRoot 'onedir'),
        '--specpath', (Join-Path $BuildRoot 'specs/onedir'), $EntryPoint
    ))

    $SingleExe = Join-Path $DistRoot 'pwcheck.exe'
    $FolderExe = Join-Path $DistRoot 'folder/pwcheck/pwcheck.exe'
    foreach ($Exe in @($SingleExe, $FolderExe)) {
        $Info = (Get-Item -LiteralPath $Exe).VersionInfo
        if ($Info.FileVersion -ne $Version -or $Info.ProductVersion -ne $Version) {
            throw 'Built executable version resources do not match the package.'
        }
    }
    $Zip = Join-Path $DistRoot 'pwcheck-folder.zip'
    Compress-Archive -Path (Join-Path $DistRoot 'folder/pwcheck') -DestinationPath $Zip
    $Checksums = foreach ($Artifact in @($SingleExe, $Zip)) {
        $Hash = (Get-FileHash -LiteralPath $Artifact -Algorithm SHA256).Hash.ToLowerInvariant()
        '{0}  {1}' -f $Hash, [IO.Path]::GetFileName($Artifact)
    }
    Set-Content -LiteralPath (Join-Path $DistRoot 'SHA256SUMS.txt') -Value $Checksums -Encoding ascii
    Write-Host "Built pwcheck ${Version}: pwcheck.exe, pwcheck-folder.zip, SHA256SUMS.txt"
}
finally {
    $env:TEMP = $PreviousTemp
    $env:TMP = $PreviousTmp
    $env:PYINSTALLER_CONFIG_DIR = $PreviousPyInstallerConfig
    Pop-Location
}

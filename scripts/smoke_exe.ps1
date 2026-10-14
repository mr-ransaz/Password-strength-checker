#Requires -Version 7.4
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$Python = Join-Path $RepoRoot '.venv/Scripts/python.exe'
$DistRoot = Join-Path $RepoRoot 'dist'
$SmokeRoot = Join-Path $RepoRoot 'build/smoke-cwd'
$Weak = 'Password1!' # Public synthetic fixtures, never account credentials.
$Strong = 'orbit velvet canyon lantern'

function Invoke-ExeCheck {
    param(
        [string] $Executable,
        [string[]] $Arguments,
        [string] $InputText,
        [int] $ExpectedCode,
        [string] $Label
    )
    $StartInfo = [Diagnostics.ProcessStartInfo]::new()
    $StartInfo.FileName = $Executable
    # Every executable check runs outside the project root.
    $StartInfo.WorkingDirectory = $SmokeRoot
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true
    $StartInfo.RedirectStandardInput = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $StartInfo.StandardInputEncoding = [Text.UTF8Encoding]::new($false)
    foreach ($Argument in $Arguments) { $StartInfo.ArgumentList.Add($Argument) }
    foreach ($Name in @('PYTHONHOME', 'PYTHONPATH', 'VIRTUAL_ENV')) {
        $StartInfo.Environment.Remove($Name) | Out-Null
    }
    $StartInfo.Environment['PATH'] = Join-Path $env:SystemRoot 'System32'
    $StartInfo.Environment['TEMP'] = $SmokeRoot
    $StartInfo.Environment['TMP'] = $SmokeRoot
    $Process = [Diagnostics.Process]::new()
    $Process.StartInfo = $StartInfo
    try {
        if (-not $Process.Start()) { throw 'Unable to start the smoke executable.' }
        $StdoutTask = $Process.StandardOutput.ReadToEndAsync()
        $StderrTask = $Process.StandardError.ReadToEndAsync()
        if ($Arguments -contains '--stdin') {
            $Process.StandardInput.WriteLine($InputText)
        }
        $Process.StandardInput.Close()
        if (-not $Process.WaitForExit(30000)) {
            $Process.Kill($true)
            $Process.WaitForExit()
            throw 'Executable smoke check timed out.'
        }
        $Stdout = $StdoutTask.GetAwaiter().GetResult()
        $Stderr = $StderrTask.GetAwaiter().GetResult()
        if ($Stdout.Contains($Weak) -or $Stderr.Contains($Weak) -or
            $Stdout.Contains($Strong) -or $Stderr.Contains($Strong)) {
            throw 'Executable output echoed a synthetic password; output withheld.'
        }
        if ($Process.ExitCode -ne $ExpectedCode -or $Stderr.Length -ne 0) {
            throw "Executable smoke check failed: $Label (output withheld)."
        }
        Write-Host "PASS: $Label (exit $ExpectedCode; no password echo)"
        return $Stdout
    }
    finally {
        $Process.Dispose()
    }
}

if (-not $IsWindows -or -not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw 'Windows and the project virtualenv are required for the smoke script.'
}
Push-Location $RepoRoot
try {
    $Version = & $Python -m scripts.windows_version --print-version
    if ($LASTEXITCODE -ne 0) { throw 'Unable to read source package version.' }
    $Version = $Version.Trim()
    $ExpectedNames = @('pwcheck.exe', 'pwcheck-folder.zip')
    $Lines = @(Get-Content -LiteralPath (Join-Path $DistRoot 'SHA256SUMS.txt'))
    if ($Lines.Count -ne 2) { throw 'Expected exactly two SHA-256 checksum entries.' }
    $Seen = @()
    foreach ($Line in $Lines) {
        if ($Line -notmatch '^([a-f0-9]{64})  (pwcheck\.exe|pwcheck-folder\.zip)$') {
            throw 'Invalid checksum entry.'
        }
        $ExpectedHash = $Matches[1]
        $Name = $Matches[2]
        if ($Name -in $Seen -or $Name -notin $ExpectedNames) { throw 'Unexpected checksum filename.' }
        $Seen += $Name
        $ActualHash = (Get-FileHash -LiteralPath (Join-Path $DistRoot $Name) -Algorithm SHA256).Hash
        if ($ActualHash -ine $ExpectedHash) { throw 'Artifact SHA-256 mismatch.' }
    }
    New-Item -ItemType Directory -Path $SmokeRoot -Force | Out-Null
    $Unpacked = Join-Path $SmokeRoot 'unpacked'
    Expand-Archive -LiteralPath (Join-Path $DistRoot 'pwcheck-folder.zip') -DestinationPath $Unpacked -Force
    $Executables = @(
        @{ Label = 'one-file'; Path = (Join-Path $DistRoot 'pwcheck.exe') },
        @{ Label = 'one-folder'; Path = (Join-Path $DistRoot 'folder/pwcheck/pwcheck.exe') },
        @{ Label = 'unzipped folder'; Path = (Join-Path $Unpacked 'pwcheck/pwcheck.exe') }
    )
    foreach ($Item in $Executables) {
        $Info = (Get-Item -LiteralPath $Item.Path).VersionInfo
        if ($Info.FileVersion -ne $Version -or $Info.ProductVersion -ne $Version) {
            throw 'Executable version metadata mismatch.'
        }
        $ReportedVersion = Invoke-ExeCheck -Executable $Item.Path -Arguments @('--version') `
            -ExpectedCode 0 -Label "$($Item.Label) version"
        if ($ReportedVersion.Trim() -ne "pwcheck $Version") { throw 'Executable CLI version mismatch.' }
        $WeakReport = Invoke-ExeCheck -Executable $Item.Path -Arguments @('--stdin', '--json') `
            -InputText $Weak -ExpectedCode 1 -Label "$($Item.Label) weak stdin"
        $WeakResult = $WeakReport | ConvertFrom-Json
        if ($WeakResult.score -ne 0 -or 'common_password' -notin $WeakResult.findings.kind) {
            throw 'Weak-password smoke analysis or bundled dictionary failed.'
        }
        $StrongReport = Invoke-ExeCheck -Executable $Item.Path -Arguments @('--stdin', '--json') `
            -InputText $Strong -ExpectedCode 0 -Label "$($Item.Label) strong stdin"
        if (($StrongReport | ConvertFrom-Json).score -ne 4) { throw 'Strong-password smoke analysis failed.' }
    }
    Write-Host 'PASS: SHA-256, PE versions, packaged dictionary, and alternate working directory.'
}
finally {
    Pop-Location
}

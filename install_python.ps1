$ErrorActionPreference = "Stop"

$osVersion = [Environment]::OSVersion.Version
$legacyWindows = $osVersion.Major -lt 10
$is64Bit = ($env:PROCESSOR_ARCHITECTURE -eq "AMD64") -or ($env:PROCESSOR_ARCHITEW6432 -eq "AMD64")

if ($legacyWindows) {
    # Python 3.8.10 is the last official release that supports Windows 7.
    $pythonVersion = "3.8.10"
} else {
    $pythonVersion = "3.11.9"
}

if ($is64Bit) {
    $installerSuffix = "amd64"
} else {
    $installerSuffix = ""
}

if ($installerSuffix) {
    $installerName = "python-$pythonVersion-$installerSuffix.exe"
} else {
    $installerName = "python-$pythonVersion.exe"
}

$installerUrl = "https://www.python.org/ftp/python/$pythonVersion/$installerName"
$installerPath = Join-Path $env:TEMP $installerName
$downloadUrls = @(
    $installerUrl,
    "https://mirrors.tuna.tsinghua.edu.cn/python/$pythonVersion/$installerName",
    "https://mirrors.bfsu.edu.cn/python/$pythonVersion/$installerName"
)

function Find-Python {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python310\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python39\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python38\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python37\python.exe"),
        (Join-Path $env:ProgramFiles "Python313\python.exe"),
        (Join-Path $env:ProgramFiles "Python312\python.exe"),
        (Join-Path $env:ProgramFiles "Python311\python.exe"),
        (Join-Path $env:ProgramFiles "Python310\python.exe"),
        (Join-Path $env:ProgramFiles "Python39\python.exe"),
        (Join-Path $env:ProgramFiles "Python38\python.exe"),
        (Join-Path $env:ProgramFiles "Python37\python.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            & $candidate -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 7) else 1)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        }
    }
    return $null
}

$existing = Find-Python
if ($existing) {
    Write-Host "Python is already available: $existing"
    exit 0
}

if (-not $legacyWindows) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Host "Trying winget..."
        & $winget.Source install --id Python.Python.3.11 -e --source winget `
            --silent --accept-package-agreements --accept-source-agreements
        $installed = Find-Python
        if ($installed) {
            Write-Host "Python installed: $installed"
            exit 0
        }
    }
}

$downloaded = $false
if ((Test-Path -LiteralPath $installerPath) -and ((Get-Item -LiteralPath $installerPath).Length -gt 1000000)) {
    Write-Host "Using the existing Python installer: $installerPath"
    $downloaded = $true
}

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
} catch {
    # Older Windows installations may rely on an updated system TLS provider.
}

if (-not $downloaded) {
    foreach ($downloadUrl in $downloadUrls) {
        Write-Host "Trying to download Python $pythonVersion from:"
        Write-Host "  $downloadUrl"
        Remove-Item -LiteralPath $installerPath -Force -ErrorAction SilentlyContinue
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add("User-Agent", "WeChat-Barcode-Scanner")
        try {
            $webClient.DownloadFile($downloadUrl, $installerPath)
            if ((Test-Path -LiteralPath $installerPath) -and ((Get-Item -LiteralPath $installerPath).Length -gt 1000000)) {
                $downloaded = $true
                break
            }
        } catch {
            Write-Host "Download failed, trying the next source."
        } finally {
            $webClient.Dispose()
        }
    }
}

if (-not $downloaded) {
    Remove-Item -LiteralPath $installerPath -Force -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "Could not download Python automatically."
    Write-Host "The official download page will now open in your browser."
    Write-Host "Install Python and tick: Add Python 3.8 to PATH"
    Write-Host "Then run START-FOR-WINDOWS.bat again."
    try {
        Start-Process $installerUrl
    } catch {
        Write-Host "Open this address manually:"
        Write-Host $installerUrl
    }
    exit 1
}

if (Get-Command Get-AuthenticodeSignature -ErrorAction SilentlyContinue) {
    $signature = Get-AuthenticodeSignature -FilePath $installerPath
    if ($signature.Status -ne "Valid") {
        Remove-Item -LiteralPath $installerPath -Force -ErrorAction SilentlyContinue
        Write-Host "The downloaded Python installer did not have a valid signature."
        exit 1
    }
}

$process = Start-Process -FilePath $installerPath `
    -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_pip=1" `
    -Wait -PassThru
Remove-Item -LiteralPath $installerPath -Force -ErrorAction SilentlyContinue

if (($process.ExitCode -ne 0) -and ($process.ExitCode -ne 3010)) {
    Write-Host "Python installer exited with code $($process.ExitCode)."
    exit 1
}

$installed = Find-Python
if (-not $installed) {
    Write-Host "Python installation completed, but python.exe was not found."
    exit 1
}

Write-Host "Python installed: $installed"
exit 0

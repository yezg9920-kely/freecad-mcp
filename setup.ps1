param(
    [string]$FreeCADPath = "",
    [switch]$SkipConfig = $false
)

$ErrorActionPreference = "Stop"

# --- Auto-detect FreeCAD console binary --------------------------------------
$commonFreeCADPaths = @(
    "D:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe",
    "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe",
    "C:\Program Files\FreeCAD 0.21\bin\freecadcmd.exe",
    "C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe"
)

$freecadCmd = $null
if ($FreeCADPath) {
    if (Test-Path $FreeCADPath) {
        $freecadCmd = $FreeCADPath
    } else {
        Write-Error "Provided FreeCAD path not found: $FreeCADPath"
        exit 1
    }
} else {
    foreach ($p in $commonFreeCADPaths) {
        if (Test-Path $p) {
            $freecadCmd = $p
            break
        }
    }
}

if (-not $freecadCmd) {
    Write-Error @"
Could not find freecadcmd.exe. Install FreeCAD 1.1 or 0.21, or pass -FreeCADPath.
Searched:
  D:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe
  C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe
  C:\Program Files\FreeCAD 0.21\bin\freecadcmd.exe
"@
    exit 1
}

Write-Host "Found FreeCAD console binary: $freecadCmd" -ForegroundColor Green

# --- Clone freecad-ai addon if missing ---------------------------------------
$addonDir = Join-Path $env:APPDATA "FreeCAD\Mod\freecad-ai"
if (-not (Test-Path $addonDir)) {
    Write-Host "Cloning freecad-ai addon into $addonDir ..." -ForegroundColor Cyan
    git clone --depth 1 https://github.com/ghbalf/freecad-ai.git $addonDir
} else {
    Write-Host "freecad-ai addon already present at $addonDir; skipping clone." -ForegroundColor Yellow
}

$entryPoint = Join-Path $addonDir "mcp_server_entry.py"
if (-not (Test-Path $entryPoint)) {
    Write-Error "freecad-ai addon is missing mcp_server_entry.py. Check the clone."
    exit 1
}

# --- Python requirements (freecad-ai has no external deps) -------------------
# If a requirements.txt appears in the addon in the future, uncomment this:
# pip install -r (Join-Path $addonDir "requirements.txt")
Write-Host "No external Python dependencies required for freecad-ai." -ForegroundColor Green

# --- Register MCP server in client configs ------------------------------------
if (-not $SkipConfig) {
    $serverCommand = Join-Path $PSScriptRoot "freecad_mcp_server.py"
    $serverConfig = @{
        command = "python"
        args    = @($serverCommand)
    }
    $serverEntry = @{ freecad = $serverConfig }

    # Write the JSON to a temp file so we do not hit PowerShell quoting issues
    # when passing a double-quoted JSON string to a native command.
    # Use [System.IO.File]::WriteAllText to guarantee a BOM-less UTF-8 file.
    $tempConfigFile = [System.IO.Path]::GetTempFileName()
    $jsonString = $serverEntry | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText($tempConfigFile, $jsonString, [System.Text.UTF8Encoding]::new($false))

    $installHelper = Join-Path $PSScriptRoot "install_mcp_config.py"

    Write-Host "Registering MCP server for Kimi ..." -ForegroundColor Cyan
    python $installHelper --client kimi --server-config-file $tempConfigFile

    Write-Host "Registering MCP server for Claude ..." -ForegroundColor Cyan
    python $installHelper --client claude --server-config-file $tempConfigFile

    Remove-Item -Path $tempConfigFile -Force -ErrorAction SilentlyContinue
}

# --- Summary ------------------------------------------------------------------
Write-Host @"

Setup complete.

FreeCAD command : $freecadCmd
freecad-ai addon: $addonDir
MCP launcher    : $(Join-Path $PSScriptRoot "freecad_mcp_server.py")

The server has been registered for Kimi and Claude if -SkipConfig was not set.
Restart your MCP client to load the FreeCAD tools.
"@ -ForegroundColor Green

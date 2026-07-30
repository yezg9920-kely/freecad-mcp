# FreeCAD MCP Server

[中文说明](README.zh-CN.md)

A tiny Windows launcher that turns FreeCAD into a headless MCP server for Kimi, Claude, and Codex via the [freecad-ai](https://github.com/ghbalf/freecad-ai) addon.

## What this package does

`freecad_mcp_server.py` locates FreeCAD's `freecadcmd.exe` and the `freecad-ai` addon, then runs the addon's `mcp_server_entry.py` so CAD clients can call FreeCAD tools through the MCP protocol.

## Prerequisites

- Windows 10/11
- FreeCAD 1.1 or 0.21 installed in one of the default paths:
  - `D:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe`
  - `C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe`
  - `C:\Program Files\FreeCAD 0.21\bin\freecadcmd.exe`
- Python 3.x (used only by the config helper)
- `git` in your PATH (for `setup.ps1`)

## Quick install

Open PowerShell in this folder and run:

```powershell
./setup.ps1
```

This will:

1. Find your FreeCAD `freecadcmd.exe`.
2. Clone `https://github.com/ghbalf/freecad-ai` into `%APPDATA%\FreeCAD\Mod\freecad-ai` (if not already present).
3. Register the MCP server in `~/.kimi/mcp.json` and `~/.claude/settings.json`.

## Manual install

If you prefer to do it by hand:

1. Clone or copy the freecad-ai addon:

   ```powershell
   git clone --depth 1 https://github.com/ghbalf/freecad-ai.git "$env:APPDATA\FreeCAD\Mod\freecad-ai"
   ```

2. Add this MCP server to your client config.

   For Kimi (`~/.kimi/mcp.json`):

   ```json
   {
     "mcpServers": {
       "freecad": {
         "command": "python",
         "args": [
           "<repo>\\freecad_mcp_server.py"
         ]
       }
     }
   }
   ```

   For Claude (`~/.claude/settings.json`):

   ```json
   {
     "mcpServers": {
       "freecad": {
         "command": "python",
         "args": [
           "<repo>\\freecad_mcp_server.py"
         ]
       }
     }
   }
   ```

   Replace `<repo>` with the absolute path to this package folder.

3. Restart the client.

## How to use from Kimi / Claude

Once the server is running, prompts like these work:

- "Create a 50 mm cube in FreeCAD."
- "Sketch a 20 mm circle on the XY plane and extrude it to 10 mm."
- "Export the current body as STEP to `D:/output/part.step`."
- "List all open FreeCAD documents and their objects."

The freecad-ai addon exposes roughly **53 tools** covering PartDesign primitives, sketches, assemblies, variables, datum geometry, fillets/chamfers, patterns, mirrors, export (STEP/STL/IGES), and document inspection.

## Example: hexacopter project

A sample FreeCAD hexacopter project is included under `examples/hexacopter`. It builds a six-rotor frame using parametric scripts.

To run it inside FreeCAD, use the addon's `execute_code` tool to run the Python scripts, e.g.:

```python
exec(open(r'<repo>\examples\hexacopter\assemble.py').read())
```

or import individual modules:

```python
import sys
sys.path.append(r'<repo>\examples\hexacopter')
import spec
import assemble
assemble.build_hexacopter()
```

Replace `<repo>` with the absolute path to this package folder.

## Boundaries and limitations

- **Console mode only:** FreeCAD runs via `freecadcmd.exe`, so viewport tools such as `capture_viewport` and `set_view` may not produce visible renders.
- **Execution timeout:** The `execute_code` tool runs inside FreeCAD's console. Long-running or blocking Python code may hit the MCP client's ~30-second sandbox timeout; prefer native freecad-ai tools when possible.
- **Windows only:** Auto-detection of FreeCAD paths is limited to common Windows installation directories. On Linux or macOS you must edit `freecad_mcp_server.py` manually.
- **No GUI event loop:** Tools that require the FreeCAD GUI (interactive selections, modal dialogs, etc.) are not available.
- **parts_library addon not included:** This package does not ship third-party part libraries.

## Files

- `freecad_mcp_server.py` — MCP server launcher.
- `setup.ps1` — One-command installer.
- `install_mcp_config.py` — JSON-safe config merger for Kimi/Claude.
- `examples/hexacopter/` — Parametric hexacopter example from `freecad_hexa`.
- `.gitignore` — Excludes caches, logs, and FreeCAD build artifacts.

## License

The launcher scripts in this package are MIT-licensed. The `freecad-ai` addon and the `examples/hexacopter` code retain their original authors' licenses.

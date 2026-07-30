#!/usr/bin/env python3
"""FreeCAD MCP launcher for Kimi / Claude / Codex clients.

This script locates FreeCAD's console binary and the freecad-ai addon, then
delegates to the addon's MCP entry point. It is intentionally tiny so it can
be registered directly as an MCP server command in client settings.
"""
import os
import subprocess
import sys


def find_freecadcmd():
    """Return the first existing freecadcmd.exe from common install paths."""
    candidates = [
        r"D:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe",
        r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe",
        r"C:\Program Files\FreeCAD 0.21\bin\freecadcmd.exe",
        r"C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe",
    ]

    # Allow user override via environment variable.
    env_path = os.environ.get("FREECAD_CMD")
    if env_path:
        candidates.insert(0, env_path)

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def find_freecad_ai_addon():
    """Return the path to the freecad-ai addon directory."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    addon_dir = os.path.join(appdata, "FreeCAD", "Mod", "freecad-ai")
    entry = os.path.join(addon_dir, "mcp_server_entry.py")
    if os.path.isfile(entry):
        return addon_dir
    return None


def main():
    freecadcmd = find_freecadcmd()
    addon_dir = find_freecad_ai_addon()

    if freecadcmd is None:
        print(
            "ERROR: Could not find freecadcmd.exe.\n"
            "Expected one of:\n"
            "  D:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe\n"
            "  C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe\n"
            "  C:\\Program Files\\FreeCAD 0.21\\bin\\freecadcmd.exe\n"
            "Set FREECAD_CMD to override, or run setup.ps1 to install FreeCAD / freecad-ai.",
            file=sys.stderr,
        )
        sys.exit(1)

    if addon_dir is None:
        print(
            "ERROR: Could not find the freecad-ai addon.\n"
            "Expected: %APPDATA%\\FreeCAD\\Mod\\freecad-ai\\mcp_server_entry.py\n"
            "Run setup.ps1 to clone https://github.com/ghbalf/freecad-ai.",
            file=sys.stderr,
        )
        sys.exit(1)

    entry_script = os.path.join(addon_dir, "mcp_server_entry.py")
    print(f"Launching FreeCAD MCP server from {addon_dir}", file=sys.stderr)
    print(f"Using FreeCAD console binary: {freecadcmd}", file=sys.stderr)

    # Run freecadcmd with the addon entry point in the addon directory so
    # relative imports and resource loading work correctly.
    sys.exit(subprocess.call([freecadcmd, entry_script], cwd=addon_dir))


if __name__ == "__main__":
    main()

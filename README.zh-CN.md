# FreeCAD MCP Server（中文版）

这是一个用于在 Windows 上将 FreeCAD 接入 MCP（Model Context Protocol）协议的小型启动器。它会自动查找 FreeCAD 的 `freecadcmd.exe` 并加载 [freecad-ai](https://github.com/ghbalf/freecad-ai) 插件，使 Kimi、Claude、Codex 等 AI 客户端能够通过 MCP 调用 FreeCAD 的参数化建模工具。

## 这个项目能做什么

`freecad_mcp_server.py` 负责：
- 自动定位 FreeCAD 安装目录下的 `freecadcmd.exe`。
- 检查并克隆 `freecad-ai` 插件到 `%APPDATA%\FreeCAD\Mod\freecad-ai`。
- 启动 `freecad-ai` 的 MCP 入口脚本 `mcp_server_entry.py`。

最终你可以在 MCP 客户端里用自然语言让 AI 控制 FreeCAD。

## 前置要求

- Windows 10/11
- FreeCAD 1.1 或 0.21，安装在以下任一默认路径：
  - `D:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe`
  - `C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe`
  - `C:\Program Files\FreeCAD 0.21\bin\freecadcmd.exe`
- Python 3.x（仅配置助手使用）
- `git` 在 PATH 中（`setup.ps1` 会用它克隆 freecad-ai）

## 快速安装

在 PowerShell 中进入本目录并运行：

```powershell
.\setup.ps1
```

它会完成：
1. 查找 FreeCAD 的 `freecadcmd.exe`。
2. 克隆 `freecad-ai` 插件（如果尚未安装）。
3. 在 `~/.kimi/mcp.json` 和 `~/.claude/settings.json` 中注册 MCP server。

完成后重启你的 MCP 客户端。

## 手动安装

1. 克隆 freecad-ai 插件：

   ```powershell
   git clone --depth 1 https://github.com/ghbalf/freecad-ai.git "$env:APPDATA\FreeCAD\Mod\freecad-ai"
   ```

2. 在 MCP 客户端配置里添加：

   ```json
   {
     "mcpServers": {
       "freecad": {
         "command": "python",
         "args": [
           "<仓库绝对路径>\\freecad_mcp_server.py"
         ]
       }
     }
   }
   ```

   把 `<仓库绝对路径>` 替换为实际路径。

3. 重启客户端。

## 使用示例

服务器启动后，可以这样提问：

- “在 FreeCAD 里创建一个 50 mm 的立方体。”
- “在 XY 平面上画一个直径 20 mm 的圆，并拉伸成 10 mm 高。”
- “把当前零件导出为 STEP 文件到 D:/output/part.step。”
- “列出当前所有打开的 FreeCAD 文档和对象。”

freecad-ai 插件大约暴露了 **53 个工具**，覆盖：PartDesign 基础体、草图、装配、变量、基准几何、倒角/圆角、阵列、镜像、导出（STEP/STL/IGES）以及文档检查等。

## 示例项目：六旋翼无人机

`examples/hexacopter/` 下包含一个参数化六旋翼机架示例。可以在 FreeCAD 中通过 `execute_code` 工具运行：

```python
exec(open(r'<仓库绝对路径>\examples\hexacopter\assemble.py').read())
```

或按模块导入：

```python
import sys
sys.path.append(r'<仓库绝对路径>\examples\hexacopter')
import spec
import assemble
assemble.build_hexacopter()
```

## 功能边界与限制

- **仅控制台模式：** FreeCAD 通过 `freecadcmd.exe` 启动，`capture_viewport`、`set_view` 等视口工具不会产生可见渲染。
- **执行超时：** `execute_code` 在 FreeCAD 控制台内运行，长时间或阻塞代码可能触发 MCP 客户端约 30 秒的超时；尽量使用 freecad-ai 原生工具。
- **仅 Windows：** 自动路径检测只覆盖常见 Windows 安装目录；Linux/macOS 需手动编辑 `freecad_mcp_server.py`。
- **无 GUI 事件循环：** 依赖 FreeCAD GUI 的工具（交互选择、模态对话框等）不可用。
- **不含零件库：** 本包不附带第三方零件库，`insert_part_from_library` 等工具在没有额外安装零件库时会失败。

## 文件说明

- `freecad_mcp_server.py` — MCP server 启动器
- `setup.ps1` — 一键安装脚本
- `install_mcp_config.py` — 安全合并 Kimi/Claude 配置的 JSON 助手
- `examples/hexacopter/` — 参数化六旋翼示例
- `.gitignore` — 排除缓存、日志和 FreeCAD 构建产物

## 许可证

本包中的启动脚本使用 MIT 许可证。`freecad-ai` 插件和 `examples/hexacopter` 代码保留原作者的许可证。

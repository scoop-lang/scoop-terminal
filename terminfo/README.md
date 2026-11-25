# Scoop terminal profile

`scoop.terminfo` 与核心 XTGETTCAP 回包均从 `data/terminal-capabilities.json` 生成。更新已实现的能力后运行 `python3 tools/generate_capabilities.py`；`--check` 检查两份产物一致，临时格式化文件自动清理。生成过程使用 `~/.scoop/bin/scoop fmt`，可通过 `--scoop` 指定工具链。

在 Unix 宿主及需要运行 TUI 的远端分别安装：

```sh
tic -x -o "$HOME/.terminfo" terminfo/scoop.terminfo
TERM=scoop-terminal command
```

能力表只声明组件已经实现的 VT、颜色和传统按键。XTGETTCAP 的 `TN` 返回组件 profile 名；不会因为系统碰巧安装了其他终端的 terminfo 就继承其扩展。图形探测将依据实际启用的解码和绘制能力独立回复。

嵌入方负责为 PTY 设置 `TERM`。未安装此 profile 时可临时使用 `xterm-256color` 获得常见 TUI 的基础行为，但该系统 profile 可能包含本组件没有实现的扩展；应用应通过 DECRQM、DECRQSS 或特定协议探测扩展，不能仅凭回退名称认定全部支持。Windows ConPTY 不要求本机 terminfo；连接 Unix 远端时仍需要安装远端 profile。demo 的外围功能和默认配置在组件完成后统一更新。

Unicode 分段、上下文宽度及 ambiguous 属性均固定为工具链的 Unicode 17.0.0。默认 ambiguous 为一列，创建终端时可显式选择两列。

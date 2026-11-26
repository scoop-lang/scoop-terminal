# 兼容性与实机验证

组件使用工具链的 Unicode 17 字素分段、宽度与分词数据。核心支持范围及明确取舍见 [组件设计](terminal-component-design.md)，性能和资源计量见 [性能报告](performance.md)。本页区分协议回放、生产 PTY 会话和真实窗口证据；一次通过不代表某个外部终端的所有扩展均已实现。

## 本机实际应用

macOS 27.2.1 / Apple Silicon，Scoop `0.0.0-dev.20261126`，编译器 `bb295704d`，开发 sysroot 包含本轮已合并的底层修复。原始结果、程序版本及启动参数保存在 [应用记录](compatibility-applications.json)；其中临时目录已规范化成 `<temporary>`。

`tools/smoke_terminal.py` 为每次运行创建临时配置、输入文件和 terminfo，使用生产 `TerminalModel`、`TerminalEmulatorSession` 与真实 PTY。每项检查子进程成功退出、宽字符头尾格配对、诊断为空，并在关闭后检查 model worker 已停止。

| 程序 | 已验证行为 |
| --- | --- |
| Bash 5.3.20 | readline 左移、插入、End、Enter；窗口 resize 后 `stty size` 与模型一致 |
| Vim 9.1 / Neovim 0.12.6 | 无用户插件的文件显示、应用自身交互搜索、中文／组合字素、resize 与退出 |
| less 668 | 搜索、resize、跳至文件末尾、退出 |
| tmux 3.8 | 独立 server 内 readline、包含状态栏的尺寸更新；显式 DCS passthrough 发送 Kitty direct graphics |
| Kitty 0.51.0 `icat` | inline stream PNG 发送、真实生产 decoder、图片与 placement 数量和像素 |
| libsixel 1.10.5 `img2sixel` | 实际编码器生成 Sixel、图片与 placement 数量和像素；颜色允许该编码器的调色板量化 |
| Bash 进度脚本 | CR／EL 刷新、OSC 9;4 事件顺序、100% 最终文字与 inactive 结束状态 |

上述八项均使用 `TERM=scoop-terminal`。另以 `TERM=xterm-256color` 通过 Bash 和 Neovim 两项回退检查。tmux 记录只覆盖显式 direct-graphics passthrough，不包括 Unicode placeholders。Vim／less 的搜索属于测试中的子进程行为，组件仍只提供搜索 API、定位和高亮。

复现（从仓库根目录）：

```sh
python3 tools/smoke_terminal.py \
  --scoop ~/.scoop/bin/scoop --sysroot ../scoop/sysroot \
  --sixel ~/repos/scoop-dep/terminal-smoke-libsixel-1.10.5/install/bin/img2sixel \
  --output /tmp/scoop-terminal-applications.json

python3 tools/smoke_terminal.py \
  --scoop ~/.scoop/bin/scoop --sysroot ../scoop/sysroot \
  --term xterm-256color --cases shell nvim \
  --output /tmp/scoop-terminal-fallback.json
```

libsixel 是仅用于互操作测试的工具，没有加入组件运行依赖。本机使用上游 `v1.10.5`（`37026b01a0bd38634ae0a8c5017bd4671101fe08`），Meson 1.9.1，release 配置 `gd=disabled,png=enabled,jpeg=disabled,tests=disabled,libcurl=disabled`，复用已有 libpng。下载按要求使用代理，源码与构建缓存留在本机依赖目录以便复测。测试不依赖用户 shell、编辑器或 tmux 配置，临时目录和本次专用 tmux server 自动清理。

## 原生窗口与剪贴板

`scoop --sysroot ../scoop/sysroot test --release demo` 包含真实窗口 resize、PTY 光标查询、PNG ACK、退出后最终画面及独立装饰的 Accepted 帧验证。选择、清除选择和纯 OSC 133 分割线更新不会增加父布局次数。无桌面环境时不能用该项代替无窗口测试。

`TerminalNativeClipboardTest` 使用实际窗口的剪贴板 adapter，将 OSC 52 读取接入有序回复队列，验证其内容与原生读取一致、DSR 排在它之后、没有 pending 读取或错误。它只读取既有剪贴板，不替换内容，也不将内容写入日志。默认作为手动桌面测试忽略：

```sh
scoop --sysroot ../scoop/sysroot test --release terminal-ui \
  --ignored --filter TerminalNativeClipboardTest
```

macOS 已通过该项。真实 PTY 的异步 OSC 52／DSR／用户输入顺序另由 `TerminalWorkerSessionTest` 检查；原生 adapter 测试与 PTY 测试分别记录，不将二者描述为同一次端到端剪贴板测试。

参考终端回包及 Linux／Windows 的本轮结果在完成后追加。

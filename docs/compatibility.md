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

创建 `Application` 的窗口、原生剪贴板和窗口基准用例均标注 `@Test(useProcess = true)`。每个用例在独立子进程的主线程完成构造、hooks 和正文，因此完整套件不会重复初始化进程唯一的窗口应用；普通无窗口用例继续共享测试进程。完整 macOS 回归为核心 186 项、UI 97 项、demo 2 项通过，另有已单独执行的手动剪贴板、应用及性能场景。窗口基准脚本分别保存用例子进程和测试调度父进程的运行时指标。

`TerminalNativeClipboardTest` 使用实际窗口的剪贴板 adapter，将 OSC 52 读取接入有序回复队列，验证其内容与原生读取一致、DSR 排在它之后、没有 pending 读取或错误。它只读取既有剪贴板，不替换内容，也不将内容写入日志。默认作为手动桌面测试忽略：

```sh
scoop --sysroot ../scoop/sysroot test --release terminal-ui \
  --ignored --filter TerminalNativeClipboardTest
```

macOS、Linux 和 Windows 已通过该项。`TerminalWorkerSessionTest` 用可控制读写的 PTY 测试替身验证异步 OSC 52／DSR／用户输入顺序；该套件的真实 PTY 用例另外验证退出前的尾数据和最终画面。原生 adapter 与有序队列分别记录，不将它们描述为同一次端到端剪贴板测试。Linux 的 adapter 测试运行在独立 Xvfb 显示，其剪贴板初始为空。

## 参考终端的真实回包

[macOS 录制](compatibility-reference-macos.json) 来自 Kitty 0.51.0 和 Ghostty 1.4.0 的独立真实窗口／PTY。两者均关闭用户配置和 shell integration，初始网格 80×24；记录包含每次输入、完整回包及查询得到的设备像素格宽高。`tools/reference_terminal.py compare` 在相同网格和像素尺寸下回放给 Scoop 核心，不通过截图推测协议结果。

两者与组件一致的行为包括字符编辑后的 CPR、origin／上下边距、2026 查询与冻结期间的实时 CPR、OSC 8／133 穿插文字后的光标，以及 Kitty 普通查询、放置 ACK 和后续 CPR。链接／命令项在这里检查解析及光标；其元数据与选择行为由核心和视图测试验证。

实际对照发现并修正 Kitty 放置后多下移一行的问题。协议说明的字面写法是下移图片行数，但 Kitty 实现使用 `effective_num_rows - 1`，Ghostty 的实际回包一致；组件明确采用最后一行的行为。两行图片从第 2 行开始，结束 CPR 为第 3 行，随后文字落在该行。单行、分块、同步输出及两种实际像素尺寸均有回归。

其余记录中的 `identical=false` 是以下明确差异：

| 项目 | 实际差异与组件策略 |
| --- | --- |
| OSC 4 终止符 | 本次 BEL 结尾查询得到 Ghostty 的 BEL 回复；Kitty 和组件均用 ST。颜色值相同，两种终止符均合法 |
| Kitty feature query | Kitty 回显 `U=1`，组件省略未支持的 Unicode placeholders；键的顺序按协议可不同。Ghostty 1.4.0 没有识别该新 feature query，将本应忽略的 payload 当作压缩图片并返回错误 |
| Sixel | 这两个固定版本均查询返回不支持，且跳过图片；组件开启 Sixel 后有对应模式与光标行为。display mode 的 CPR 偶然相同不能视为参考终端支持 Sixel |

这里不以参考终端的多数行为覆盖规范。图片光标采用实际 Kitty 行为的取舍已写入设计；未支持的 feature query 键继续省略，标准允许的 OSC 终止符继续使用 ST。

[Linux 录制](compatibility-reference-linux.json) 来自 xterm 407 的实际 PTY，运行于独立 Xvfb X11 显示，网格 80×24、实际单元 6×13 像素。显式设置 `decTerminalID=340`、`sixelScrolling=true`、`privateColorRegisters=true`。15 组输入包括七项 Sixel 检查：80／1070／8452 模式查询、scrolling／display／rightward 模式，以及结尾 `-` 在 8452 开关下的光标、右边界换行；这些回包全部与组件一致。原始输入与回包已保存，按录制尺寸在 macOS、Linux 核心分别回放，结果一致。

xterm 的普通编辑、origin／边距及 OSC 8／133 穿插文字后的 CPR 也相同。其余差异为 OSC 4 使用 BEL 回复，以及该版本对 2026 查询返回不支持、忽略 Kitty graphics APC；没有将这些差异记作等价支持。该录制验证模式和光标位置，Sixel 像素、比例、透明度、共享调色板和擦除行为仍由核心／光栅用例验证。

录制程序必须在参考终端自己的 PTY 中运行，例如：

```sh
kitty --config NONE -o shell_integration=disabled \
  -o remember_window_size=no -o initial_window_width=80c -o initial_window_height=24c \
  -o close_on_child_death=yes \
  python3 /absolute/path/to/tools/reference_terminal.py record \
  --name Kitty --version 0.51.0 --configuration 'config NONE; shell integration disabled; initial grid 80x24' \
  --output /tmp/kitty-window.json

python3 tools/reference_terminal.py compare \
  --recordings /tmp/kitty-window.json \
  --scoop ~/.scoop/bin/scoop --sysroot ../scoop/sysroot \
  --output /tmp/terminal-reference-comparison.json
```

Ghostty 在 macOS 上经 `open -n -a Ghostty --args` 启动，设置 `--config-default-files=false --window-save-state=never --shell-integration=none --quit-after-last-window-closed=true --confirm-close-surface=false --window-width=80 --window-height=24`，再以 `-e` 运行同一录制程序。全部探测完成后子进程退出，专用参考窗口关闭；没有复用或关闭用户已有窗口。

## Linux 与 Windows 集中回归

本轮使用各机器已有的 `0.0.0-dev.20261126` 发布编译器，并在任务专用目录重建所需开发 sysroot，包含本轮已合并的 Unicode、字体、PNG 和裁剪修复。复用已有原生依赖和 runtime，不改动用户的原仓库。测试记录见 [跨平台结果](compatibility-platforms.json)；耗时包含构建，不能作为跨平台性能比较。

| 平台 | 核心 | UI | 原生窗口 | 只读剪贴板 |
| --- | --- | --- | --- | --- |
| Linux GNU x86_64，glibc 2.43 | 186 通过 | 97 通过 | 2 通过 | 1 通过 |
| Windows x64 / Microsoft UCRT | 186 通过 | 97 通过 | 2 通过 | 1 通过 |

Linux 使用 GTK X11、独立 Xvfb 显示及 `dbus-run-session`，验证 resize、实际 PTY 的 CPR／PNG ACK、最终输出、退出关闭和独立装饰的 Accepted 帧。它验证原生窗口路径，不等同于 Wayland、物理显示器时序或硬件 GPU 性能。`useProcess` 使两个原生用例分别初始化窗口应用，完整套件通过。

Windows 11 build 26300 使用 Microsoft UCRT 目标、MSVC tools 14.51.36231 和 Windows SDK 10.0.26100.0。原生窗口／剪贴板用例在已登录用户的交互桌面运行，验证 ConPTY 的焦点与输入、resize、退出码 17、最终输出保留，以及选择／OSC 133 装饰进入 Accepted 帧而不增加文字布局。两个窗口用例分别在 `useProcess` 子进程中初始化 `Application`。

首次 Windows UI 回归为 96 项通过、1 项失败：真实 ConPTY 的立即退出用例预期 7，实际为 1。已定位为 Scoop 为普通 `/d`、`/c` 参数添加不必要引号，修复合并于 [Scoop PR #232](https://github.com/scoop-lang/scoop/pull/232)，上游 Windows 进程测试 8/8 通过。更新开发 sysroot 及其下游依赖后，完整 UI 97 项、demo 2 项和只读剪贴板 1 项重新通过；未受此修复影响的核心 186 项复用此前结果，JSON 为其单独保留原 sysroot 版本。

[Linux 应用记录](compatibility-applications-linux.json) 包含 Bash 5.3.9、Neovim 0.11.6、less 668 和进度脚本，以及 Bash／Neovim 的 `xterm-256color` 回退。该机的 `vim` 命令实际指向 Neovim，因此记录保留两个命令入口及实际版本，不重复计为独立 Vim 实现；macOS 的 Vim 9.1 记录见上文。tmux 与两种图片发送工具的实际应用覆盖来自本机记录，Linux 另完成 xterm Sixel 实际回包对照。

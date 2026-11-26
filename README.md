# Scoop 终端模拟器

`scoop.terminal.emulator` 是纯 Scoop 的 VT 核心。`Terminal.feed()` 接收输出字节并更新屏幕和历史，`encodeInput()` 根据当前模式编码文本、按键、鼠标和粘贴。回包、标题和响铃以值返回，可以在无窗口环境回放测试。

`scoop.ui.terminal` 提供桌面会话和 `terminalView(session)`。在 `Application.runWithAsyncio` 的作用域中调用 `TerminalEmulatorSession.start(command)`，把视图挂到 UI 树。会话通过 `EventLoop.spawnPty()` 启动子进程，并按序写入用户输入和 VT 回包。视图处理已接受的尺寸、历史浏览、选择、剪贴板和输入法。通过 `session.reading` 读取已提交的不可变画面；需要跨更新保留内容时取得 `session.snapshot()` 并在使用结束后关闭。嵌入方负责调用 `session.close()`，自然退出后可以继续展示最后的屏幕和状态。

session 的公开调用和宿主回调在窗口 owner 上执行；VT 解析、输入编码、resize、主题和宽度切换按队列顺序交给独立 model worker。`send`、`setColors`、`setAmbiguousWidth` 都是排队操作，`reading` 反映最近一次已交付的结果。普通操作默认最多保留 1024 项／8 MiB 输入负载，包含正在执行的一项；超出时调用明确失败。PTY 每个 8 KiB 输出块等待处理和发布后才继续读，慢解码不会积累无界待处理输出。选择跟踪也通过队列注册和释放，不等待后台完成一次手势。

普通输出直接请求下一可用帧，由 UI root 合并同帧更新；同步输出仍保持其提交边界。闪烁只在有焦点、可见且运行中的视图按需计时，隐藏、遮挡、退出和卸载会取消；辅助功能内容随已接受帧更新。

组件后续改进见 [Terminal 组件改进设计](docs/terminal-component-design.md)，包含核心正确性、OSC、选择与搜索 API、字体连字、图形和性能；外围工具 UI 留给后续 demo。

组件提供 [scoop-terminal terminfo](terminfo/README.md)，与 XTGETTCAP 使用同一份能力表。核心也支持 DECRQM、DECRQSS 和字符/设备像素尺寸查询；无窗口使用者通过 `resize(..., pixels = ...)` 提供已接受的像素尺寸，未提供时像素查询报告 0。

Unicode ambiguous 字符默认占一列；创建核心／会话时可传 `ambiguousWidth = TerminalAmbiguousWidth.Wide`，运行中可调用 `setAmbiguousWidth(...)`。切换会提交同步输出并重排主备屏正文及历史，锚点继续指向原文，旧快照保留原策略；备用屏不产生历史，溢出仍按保留范围淘汰。视图接受新布局前，命中和高亮坐标继续使用旧帧。

OSC 52 默认允许写入、拒绝读取，文本上限为 1 MiB。可在创建核心或会话时传入 `TerminalClipboardPolicy(read = true)`，也可禁用写入；这不影响用户主动复制/粘贴。挂载的视图提供本机剪贴板及实际可用的 PRIMARY selection，未挂载时可通过 `start(clipboard = Some(adapter))` 注入 `TerminalClipboardAdapter`。异步读取的完成回调必须回到会话 owner，返回的 `Disposable` 用于取消；默认一秒期限、拒绝或服务不可用都会完成空回复。PTY 写队列为每个读取预留位置，后续回复和用户输入保持顺序。宿主服务错误可通过 `onHostServiceError` 观察。

`TerminalLine.cells` 是不可变 `List<TerminalCell>`，索引与 `size` 仍描述完整物理网格，尾部空单元按需表示。需要具体数组的调用者使用 `.toArray()`；历史和快照共享冻结内容，编辑时复制受影响行。

OSC 8 通过 `TerminalViewOptions(onLinkActivated = ..., onLinkHovered = ...)` 暴露宿主回调，默认使用 Ctrl+点击（macOS 为 Command+点击）激活。组件保留完整 URI，由宿主决定如何打开。

OSC 133 的 A/B/C/D 标记生成命令块，可从 `reading.commands(start, count)`、`commandAt(anchor)`、`commandsIn(range)` 读取；`reading.text(range)` 读取原文。`TerminalViewOptions(commandSeparators = true)` 开启提示符行顶部的分割线，默认关闭。组件不修改 shell 配置，标记由 shell 或程序发送。

`snapshot.search(query, TerminalSearchOptions(...))` 返回可关闭的分页字面量搜索；调用 `nextPage(maxMatches, scanBudget)`，并检查每个结果的 `status(reading)` 后定位。大小写不敏感使用完整 Unicode casefold；搜索对象拥有独立快照，关闭原快照不会取消查询。组件不包含搜索框。

`session.search(...)` 返回 `TerminalAsyncSearch`，在窗口 owner 的协程中调用挂起的 `nextPage()`；实际扫描在独立 worker 上进行，每页最多 65536 个步骤／1024 个结果，每 4096 步检查取消。取消协程或查询会释放其快照，迟到结果不交付；会话关闭等待查询退出并回收 worker。控制器的 `reveal(match, alignment)` 检查结果版本，等待相应的 Accepted 帧后完成；`rectsFor(match)` 返回可见矩形及帧版本。`setSearchHighlights(matches, active)` / `clearSearchHighlights()` 只更新绘制层，不改变文本样式或创建外围 UI。`SearchContentChanged` 通知已提交文本变化，宿主可检查旧结果或重新查询；它不表示全部旧结果已经失效。

可创建 `TerminalViewController(session)`，用 `terminalView(session, controller = Some(controller))` 挂载。控制器提供 `select(range)`、`selectAll()`、`clearSelection()`、`scroll(lines)` 和 `copySelection(options)`；`onChanged` 通知滚动、选择变化及覆盖失效。显式控制器在视图卸载后由应用关闭，未传控制器时由视图管理。所有调用仍在会话 owner 上执行。

视图支持双击按 Unicode 词选择、三击按逻辑行选择、Shift 扩展、Alt 矩形选择和越界拖动自动滚动。`TerminalViewOptions.additionalWordCharacters` 可增加路径／标识符字符。主备屏分别保留滚动与选择；矩形在重排后仍按原各行文字范围复制。`TerminalCopyOptions(trimPadding = false)` 可保留网格补齐空白，默认只去掉这些补齐格，始终保留显式输出的空格。

文字缓存持有独立字体副本，按 LRU 局部淘汰；默认最多 1024 项、16 MiB 估算权重。正在展示的帧独立持有其排版引用，淘汰不会关闭帧仍需使用的资源；字体来源更新或关闭后，旧帧的延迟光标排版仍使用原字体。

`TerminalAppearance.ligatures` 默认为 `TerminalLigatures.Enabled`，也可设为 `Disabled` 或 `AtCursor`。后者将光标所在字素与相邻文字分开排版，其他 run 继续复用。`fontFeatures` 接受 OpenType 特性；Disabled 会覆盖 `liga`、`clig`、`calt`、`dlig` 为 0，其他显式特性仍保留。连字只改变字形，复制、搜索、命中和光标继续使用终端列；不满足逐列 caret 校验的文本退回逐字素绘制。

桌面 session 默认启用 Sixel 和 Kitty 静态图片，PNG 使用后台 CPU decoder；可通过 `start(graphics = TerminalGraphicsSupport())` 关闭图形。无窗口核心默认关闭图形，嵌入方具备图片绘制能力时显式开启，并提供已接受的设备像素尺寸，PNG 另需注入 `TerminalImageDecoder`。

Sixel 支持私有／共享调色板、透明背景、像素比例、80／1070／8452 模式和能力查询。Kitty 支持 direct mode 的 RGB／RGBA／PNG、Base64 分块、Zlib、静态放置／删除／查询、源裁剪及 z 图层；图像后的文字与光标查询按同一 VT 流处理。文件和共享内存 transport、动画、Unicode placeholders、relative placements 与 f=8/16 不在本轮范围；不能把 tmux 的 placeholder 图片路径视为已支持。PNG 只向 codec 传递像素／颜色 chunks，保留有界 ICC 配置；文字和 EXIF 不展开，方向遵循 IHDR 像素网格。

`reading.images` 提供图片和 placement；跨更新使用时保留快照或调用 `images.retain()`，上传区域由 `image.pixels(region)` 返回独立租约。视图仅上传可见的 64×64 块，按 LRU 管理原生图片，默认 128 MiB 估算预算、4096 个缓存条目和每帧 8192 次 tile 准备。`TerminalViewOptions.imageCacheLimits` 调整这些上限，`onImageError` 接收每帧首次准备失败；失败的 placement 整体跳过，文字继续绘制。预算包括仍被旧帧持有的原生图片，缩小预算不会强制关闭它们。自然退出保留图片；显式关闭核心／session 释放其图片所有权，已取得的快照或原生绘制帧仍独立存活。`reading.withoutImages()` 可只保留文本和元数据。

## 开发

使用包含伪终端接口、纯文本 `scoop.charset.wordBoundaries` 及 `FontCollection.copy()` 的 Scoop 工具链。使用 Scoop 源码仓库的开发 sysroot 时显式传入其路径。

```sh
scoop --sysroot ../scoop/sysroot test --release emulator
scoop --sysroot ../scoop/sysroot test --release terminal-ui
scoop --sysroot ../scoop/sysroot run --release demo
```

示例启动本机默认 shell，可以在 `--` 后指定可执行文件和参数。在有桌面会话的 macOS、Linux GNU 或 Windows 环境运行 `scoop --sysroot ../scoop/sysroot test --release demo`，可验证真实窗口 resize 和 shell 退出后的输出。Unix 用例还检查子进程发出的 VT 光标查询。

手动性能基准、固定基线和指标边界见 [性能测量](docs/performance.md)。普通测试跳过这些测量；使用 `tools/benchmark_terminal.py --cases ...` 只重测受影响场景。

# Terminal 组件实现进度

目标是完整交付 [组件改进设计](terminal-component-design.md) 的本轮范围。此文件记录完成证据和剩余工作；部分测试通过不代表整个设计完成。

实现分支：`codex/terminal-component-foundation`。每个可验证变更提交并推送后继续。先完成本机功能与验证，再集中进行 Linux / Windows 回归。

## 工作清单

| 阶段 | 工作 | 状态 |
| --- | --- | --- |
| M1 | 分页历史、行 ID 索引、复用不可变行内容 | 已实现，核心测试通过 |
| M1 | 逻辑行、正文 reflow、宽字素、anchor 定位与淘汰/重置失效 | 已实现，核心及选择回归通过 |
| M1 | VT 编辑的 anchor 迁移、覆盖通知及消费者失效 | 有界跟踪核心与 6 项回放已完成，控制器/选择/命令已接入；图形消费者随 M5 接入 |
| M1 | 已提交快照、变化集、session reading 与消费者迁移 | 已实现，快照与视图回归通过 |
| M1 | 有界 OSC 分派、流式 DCS/APC 生命周期与解析恢复 | 已实现，解析器 6 项测试通过 |
| M1 | 上下/左右边距、矩形滚动、宽字符编辑、DECSC/DECSTR/RIS | 已实现，核心 40 项测试通过 |
| M1 | Unicode 17 字素/宽度、创建时 ambiguous 策略、变体序列与零宽前缀 | 已实现，核心 46 项测试通过 |
| M1 | 运行中修改宽度策略的全量重排 | 已实现，7 项核心与 1 项视图用例通过，完整核心 112 项／UI 54 项通过 |
| M1 | 传统键鼠、1016 像素鼠标、水平滚轮 | 已实现，5 项输入协议用例通过 |
| M1 | 下划线类型/颜色、光标形状、独立闪烁 | 已实现，4 项协议及 3 项绘制/缓存用例通过 |
| M1 | DECRQM/DECRQSS/XTGETTCAP、尺寸查询及共享 terminfo 能力表 | 已实现，5 项协议用例及生成一致性/语法检查通过；图形能力在图形阶段加入 |
| M2 | 同步输出 2026、序列边界提交、独立硬期限 | 已实现，完整核心 65 项通过；真实 PTY 期限在集中验收验证 |
| M2 | 异步宿主效果的有序回复票据 | 已实现，虚拟期限/乱序完成/关闭回归通过 |
| M2 | OSC 颜色查询/设置/重置 | 已实现，5 项协议、5 项快照及 4 项绘制/缓存用例通过 |
| M2 | OSC 8 超链接与交互 | 核心 6 项及交互/光栅 3 项通过，controller 的已接受帧 point 查询已接入 |
| M2 | OSC 52 与宿主剪贴板策略 | 已实现，4 项核心及 4 项桥接/队列用例通过；真实系统剪贴板在集中验收验证 |
| M2 | OSC 7 工作目录、9;4 进度事件 | 已实现，5 项核心用例及 UI 编译检查通过 |
| M3 | controller、高级选择、拖动滚动、复制规则 | 已实现，9 项选择、2 项期限、1 项光栅及原视口 5 项通过；真实窗口事件在集中验收验证 |
| M3 | 字面量搜索、casefold 映射、分页/取消/限额 | 核心 7 项通过，独立搜索 worker 与 4 项异步分页／关闭用例已完成 |
| M3 | reveal、矩形、高亮与结果失效 | 已实现，6 项定位与 3 项高亮/光栅验证通过 |
| M3 | OSC 133 命令块及可选分割线 | 已实现，7 项协议回放及默认开关/叠加像素验证通过 |
| M4 | 独立字体副本、LRU 与帧排版租约 | 已实现，3 项淘汰/寿命/像素及原有 4 项绘制回归通过 |
| M4 | 连字 run、逐列网格校验、字体 fallback 与装饰 | 已实现，8 项连字/退回用例及完整 UI 53 项通过；真实窗口字体更新随集中验收验证 |
| M5 | 跨线程不可变快照租约与配额 | 已实现，3 项多线程用例与原快照 5 项／搜索 7 项通过 |
| M5 | 独立搜索 worker、取消及退出 | 已实现，4 项异步用例通过；图片文本投影已验证不保留图片资源 |
| M5 | 串行后台 model 与排队跟踪 | 已接入生产 session，后台 7 项、会话 6 项及完整 UI 72 项通过 |
| M5 | 图片 store/decoder/cache、预算 | 解码／传输基础核心 11 项、UI 3 项及图片快照 4 项通过；store、生产帧交付和绘制接入待完成 |
| M5 | Sixel 编码、颜色、滚动、查询及生命周期 | 增量解码、版本化调色板及索引块已实现，13 项针对测试通过；DCS、滚动、查询与绘制接入待完成 |
| M5 | Kitty 静态 profile、分块、放置/删除/探测 | 待实现 |
| M6 | 帧调度、局部失效、缓存/批量处理及基准报告 | 待实现 |
| M6 | 本机窗口/PTY、实际应用、资源释放与错误路径 | 待实现 |
| M6 | Linux 本轮完整回归 | 待本机完成后执行 |
| M6 | Windows 本轮完整回归 | 待本机完成后执行 |

搜索框、标签页、分屏和会话管理等外围 UI 按设计留待后续 demo；Kitty 的后续扩展范围以设计第 9 节为准，不将其冒充为已支持。

## 已执行验证

- 工具链：`~/.scoop/bin/scoop`，`0.0.0-dev.20261126`，编译器 `bb295704d`。
- `scoop --sysroot ../scoop/sysroot test --release emulator`：46/46 通过，包括 8 项边距/编辑/复位、6 项解析、3 项存储、11 项 reflow、5 项快照及 6 项 Unicode 宽度测试。
- 同步输出改动后的完整 `emulator` 回归：65/65 通过。新增 5 项覆盖 feed 内多次 BSU/ESU、冻结期间查询与输入、重复 BSU 的同一期限代次、显式期限释放、EOF/resize/RIS 及旧历史快照隔离；UI 测试代码编译检查通过。
- `scoop --sysroot ../scoop/sysroot test --release emulator --filter InputProtocolTest`：5/5 通过，覆盖 Ctrl 别名、修饰功能键/方向键、小键盘、X10/传统原始字节、跟踪/编码独立切换、1016 像素及横向滚轮。视图从已接受布局的设备缩放计算像素坐标；未接受尺寸或 DPI 不用于鼠标报告。
- `scoop --sysroot ../scoop/sysroot test --release emulator --filter RenditionTest`：4/4 通过，覆盖 4:0..5、21/24、58/59、无效色彩空间、DECSCUSR、光标可见性/闪烁独立及保存恢复。
- `scoop --sysroot ../scoop/sysroot test --release emulator --filter CapabilityQueryTest`：5/5 通过，覆盖流顺序中的真实模式、SGR 回包回放、分块/取消/上限、未知查询失败及像素变化保留边距。UI 测试代码编译检查通过。
- `python3 tools/generate_capabilities.py --check` 与 `tic -x -c terminfo/scoop.terminfo`：通过；查询和安装 profile 来自同一能力表，生成临时文件自动清理。
- `scoop --sysroot ../scoop/sysroot test --release emulator --filter OscColorTest`：5/5 通过；`SnapshotTest` 5/5 通过；绘制/缓存 4/4 通过。覆盖 16-bit 查询、X11 `#` 高位与 `rgb:` 比例转换、批量参数、当前主题重置、独立的显式 RGB、冻结颜色及实际像素；快照配额已计入完整调色板的保守占用。
- OSC 52：核心 `ClipboardProtocolTest` 4/4、UI `ClipboardBridgeTest` 4/4 通过。覆盖默认拒绝读取、禁写、严格 Base64/UTF-8、空内容清空、字节限额、目标顺序、有序 PTY 票据、异步乱序完成、虚拟一秒期限、卸载/关闭后迟到结果、无服务、异常及最多 32 个待处理读取。已消费或取消的票据释放其输出字节。
- `ShellMetadataTest` 5/5 通过，覆盖 OSC 7 的远端 host/百分号路径、无效 URI、OSC 9;4 缺省与保留百分比、0..100 限制、冻结期间事件顺序和 EOF/RIS 清理。元数据计入快照配额；组件没有目录访问、通知、任务栏或进度工具 UI。
- OSC 8 核心 `HyperlinkTest` 6/6 通过；由于链接引用回收覆盖全部屏幕编辑路径，本次完整核心回归 85/85 通过。覆盖任意字节切分、参数保留、显式 ID 分组、宽格尾部、重排、矩形滚动、淘汰、保存光标与旧快照隔离；按记录数/字节限额拒绝新链接并产生诊断。链接记录保存在共享不可变索引中，单元格仅存 ID，已提交快照计入相应保守占用。
- `TerminalLinkInteractionTest` 3/3 通过，覆盖已接受帧的链接命中、宽字符尾列、拖动阈值/取消/越界/不同链接不激活，以及显式 ID 多片段悬停的实际像素。`TerminalViewOptions` 提供 `onLinkActivated` / `onLinkHovered`，普通点击仍选择，Ctrl/Command 修饰点击只触发回调；应用鼠标模式优先，Shift 绕过。指针 claim、取消通知及不可取消的 release 清理已接入；真实窗口事件路径留集中验收验证。
- `AnchorTrackingTest` 6/6、原有 `ReflowTest` 11/11 通过。`Terminal.track` 返回可关闭的有界注册，按受影响物理行订阅编辑；插删迁移、覆盖选区内部失效、提示符边界与显式擦除、逻辑行拆分、reflow、历史裁剪及同步冻结分别验证。已变更旧帧上的新注册明确返回 Stale；不把旧坐标套到新内容。快照保存不可变跟踪结果并计入预算；关闭/失效释放行引用，没有追加永久编辑日志。
- OSC 133：`ShellCommandTest` 7/7、`TerminalCommandSeparatorTest` 1/1 通过，并重跑锚点 6/6。覆盖 A/B/C/D、可缺省退出状态、130 状态、孤立/丢失标记、次级提示符、擦除后跨 feed 重绘去重、pending-wrap、一行无历史、重排、冻结、主备屏及 EOF/RIS。`commandAt` / `commandsIn` / 分页 `commands` 返回已提交的命令块；`reading.text(range)` 读取原文。每个 buffer 最多保留一个没有可见锚点的提示符重绘上下文；它也受命令数量与字节预算约束。默认共保留 2048 个命令记录、8 MiB 元数据，旧快照和当前状态分别计费。
- `TerminalViewOptions.commandSeparators` 默认 false；开启后只在后续主提示符所在物理行顶部画中性线，不增加行高、文字或光标移动。像素回归确认首条/次级提示符不新增线，关闭时没有线，绘制前后文字和光标相同。没有新增搜索框、命令工具栏或 shell hook 注入。
- `LiteralSearchTest` 7/7 通过。`snapshot.search` 使用流式字面量匹配，分页同时限制命中数与扫描工作量；单个长字素和空行也分步推进。覆盖跨 soft wrap、硬行边界、重叠命中、`ß`/sigma/`İ` 完整 casefold、字素内部的精确原文 UTF-8 范围、无 normalization、部分历史前缀、冻结快照语义、取消、句柄/查询/工作内存/命中上限，以及 reflow 有效、改色有效、文字覆盖 Stale 和 reset Unavailable。关闭或完成会释放查询独立快照与工作数组，工作内存纳入快照总预算；每页返回源版本、查询代次与下一扫描位置。
- 高级选择：`TerminalSelectionTest` 9/9、`TerminalSelectionScrollTest` 2/2、`TerminalSelectionPaintTest` 1/1，原视口 5/5、锚点 6/6 通过。覆盖 Unicode 词与额外路径字符、软换行逻辑行、宽字素矩形与重排后逐原行复制、显式空格/补齐策略、编辑迁移与覆盖通知、主备屏独立状态、历史裁剪后 Shift 扩展、冻结及过期帧拒绝。绝对单调期限随越界距离调速，不被连续指针移动推迟；光栅验证逐行选区而非整个包围框。`TerminalViewController` 支持显式选择、全选、滚动、复制及变更通知，关闭释放跟踪与订阅。修复旧 Accepted 帧在纯 reflow 后新注册的初始版本，以及跨宽字符软换行的跟踪范围错误保留补齐格的问题。
- 搜索视图 API：`TerminalNavigationTest` 6/6、`TerminalSearchHighlightTest` 3/3、`TerminalAsyncSearchTest` 2/2，通过后选择 9/9 回归。覆盖 Nearest/Start/Center/End、未挂载/resize/旧帧等待、滚动取消、Stale/Unavailable、冻结历史定位且不提交隐藏输出、已接受帧的 anchor/link/command 命中、重排/字素扩展、部分淘汰、普通/当前匹配实际像素、复用同一 frame 清除高亮，以及协程公平性、强制页上限和取消释放。高亮使用按逻辑行版本的区间索引，只查询可见行并合并重叠；只请求绘制帧，不重新排版文字。新增 `SearchContentChanged` 作为查询源变化通知，各结果仍独立核对状态。没有增加搜索框、按钮或结果列表。
- `scoop --sysroot ../scoop/sysroot test --release terminal-ui --filter TerminalGlyphCacheTest`：3/3 通过；新增 CPU 光栅验证检查双下划线颜色、文字隐藏阶段和光标闪烁互不混淆。文字和光标计时只请求帧，复用已经排版的内容，卸载时取消计时。
- `scoop test --release terminal-ui --filter TerminalViewportTest`：5/5 通过，包括跨 reflow 保持选区、宽字符换行补齐不进入复制内容，以及已接受帧在 resize 后仍定位原字符。
- `scoop test --release terminal-ui --filter TerminalGlyphCacheTest`：2/2 通过，包括一列宽字素的实际替代符排版。
- `scoop test --release emulator --filter ParserTest`：6/6 通过，包括每个字节边界的切分、冒号子参数/中间字节、CAN/SUB/EOF、非法 DCS header、OSC 精确上限与超限整串丢弃。
- `scoop check --release demo --tests`：通过；session 消费者已迁移到只读 `reading`。
- 快照验证覆盖旧代次隔离、共享历史页及索引、同代次配额共享、关闭释放、文本/样式/光标版本分离；快照字节配额采用保守内容估算，不等同于进程实测 RSS。
- 存储与 reflow 测试覆盖旧快照隔离、跨页淘汰/恢复、宽字素的一列占位、保存光标/样式、主备屏、逻辑边界 affinity、硬换行、实际空格及多次宽度变化。
- Scoop 底层已补齐完整字素宽度、显式 ambiguous 策略及统一的 Unicode 17 字素分段，独立提交并合并 [PR #220](https://github.com/scoop-lang/scoop/pull/220) 和 [PR #221](https://github.com/scoop-lang/scoop/pull/221)。release clippy、charset 用例、原生 ABI 均通过。开发 sysroot 已使用安装编译器完整重建，后续命令显式传 `--sysroot ../scoop/sysroot`；没有修改编译器。
- 无排版分词入口 `scoop.charset.wordBoundaries` 已在 Scoop 独立提交、推送并合并 [PR #223](https://github.com/scoop-lang/scoop/pull/223)，main 已回合并到该修复分支并推送。复用现有 ICU4X dictionary 数据，未下载新依赖；release Clippy、2 项适配、3 项原生 ABI、实际示例与 API 文档检索通过，开发 sysroot 已更新。本轮 PR 文本与局部文档临时目录已清理。

- 字体缓存：`TerminalGlyphLruTest` 3/3，原 `TerminalGlyphCacheTest` 4/4 通过。验证 LRU 最近访问、缓存满后继续复用、条目/估算字节上限、超大布局不驻留、幂等租约关闭、缓存关闭后的独立绘制，以及旧帧在淘汰和字体来源关闭后的逐像素一致性。固定官方 Fira Code 6.2，字体来源、摘要和 OFL 许可随测试保存；下载使用指定代理，依赖压缩包留在 `~/repos/scoop-dep/terminal-fonts`。
- `FontCollection.copy()` 已在 Scoop 独立分支提交并合并 [PR #224](https://github.com/scoop-lang/scoop/pull/224)，main 已回合并修复分支并推送。4 项字体集合用例、原生 `-Werror` 编译、局部 API 文档检索及关闭来源后延迟排版的实际示例通过。开发 sysroot 已更新；本轮探测程序、字体临时副本、PR 文本和局部 API 文档已清理。
- 连字：`TerminalLigatureTest` 5/5、`TerminalRunFallbackTest` 3/3，通过后完整 `terminal-ui` 53/53。实际像素对照原生 Fira Code 排版，验证 Enabled/Disabled/显式 feature 优先级、所有 caret 列、组合字素、背景/链接/装饰/选择不打断兼容 run、跨行边界、原文复制和块光标裁剪重着色。AtCursor 计数验证只新排版当前片段，移开后原行像素恢复，重复绘制命中缓存；比例字体以“总宽一致、内部不同”的反例验证退回，固定 CJK 缺字 fallback 与双宽尾格、bidi 重排也有覆盖。Roboto/CJK 字体复用本地既有资料，许可证和摘要随测试保存，没有额外下载。

运行时宽度切换已覆盖创建即 Wide、Narrow/Wide 往返、活动／保存光标及宽尾格、单列占位、历史限额、主备屏、同步输出、REP、分段 UTF-8、OSC 8/133 和既有样式。锚点使用固定 Narrow 列跨度，纯重排不增加文字版本，旧快照保留旧策略；选择与搜索原文保持，已接受帧在新布局完成前继续提供旧坐标。`RuntimeWidthPolicyTest` 7/7、`TerminalWidthPolicyViewTest` 1/1，随后完整核心 112/112、UI 54/54 通过。没有新增下载或本轮临时文件。

- 后台迁移准备：`TerminalSnapshotPool` 将不可变 reading 的保留与可变终端分开；原子更新句柄／代次／工作内存配额，单个句柄的并发关闭只退还一次。`TerminalSnapshotThreadTest` 3/3 覆盖实际 worker 上同代次共享、句柄与字节限额、100 次并发重复关闭、200 个独立查询的唯一代次和完整预算回收；原 `SnapshotTest` 5/5、`LiteralSearchTest` 7/7 通过。测试闸门曾因共用接收队列而等待错误任务，已改为独立闸门并通过；没有底层库改动或临时文件遗留。

- 搜索 worker：`TerminalAsyncSearchTest` 4/4 通过。扫描在独立单 worker 执行，每 4096 步检查取消；UI 在扫描期间只修改原子取消标志，核心查询独占交接。测试刻意阻塞 worker，确认窗口 owner 的其他任务继续推进、重复页请求被拒绝、取消后没有迟到命中，并检查闲置查询关闭、重复 shutdown、关闭后拒绝新查询及快照配额完整退还。会话关闭在不可取消的清理作用域等待查询退出与执行器停止；自然 EOF 后仍可搜索最终画面。

- 串行后台模块：`TerminalBackgroundModelTest` 7/7，通过实际不同的线程创建和执行核心，发布回到窗口 owner。验证按序 feed／输入模式／DSR／resize、工作线程阻塞时 UI 仍推进、PTY 提交等待容量、活动请求计入字节／条目限额、注册未完成即关闭、核心配额拒绝、选择迁移／覆盖失效、重复 BSU 保留起始时刻、过时代次不能解冻、关闭提交尾部及回收 worker、发布回调失败会拒绝后续等待者；还覆盖父作用域在 driver 执行前取消的清理。`TerminalTrackedRange` 改为可由 adapter 实现的所有权接口，跨线程只发送不可变注册结果与原子取消位；可变核心句柄仍由后台持有。关闭后释放可变核心和回调引用，只保留最终不可变画面。原锚点 6 项与命令块 7 项回归通过。该提交只建立并验证后台模块，生产 session 在下一步迁移。

- 生产会话已迁移到后台 model，UI 不再持有／访问可变终端；PTY I/O 和宿主回调维持窗口 owner，快照来自独立有界池。`TerminalWorkerSessionTest` 6/6：本机真实 PTY 的立即退出尾部、短写与 OSC 52／DSR／用户输入顺序、重复 resize、持续 BSU 输出期间的独立期限、自然 EOF 提交冻结文字并继续搜索／重排、driver 开始前关闭、宿主回调异常与最终画面保留。随后完整 `terminal-ui` 72/72、`scoop check --release demo --tests` 通过。本轮没有下载和临时文件；真实窗口、系统剪贴板、综合性能及 Linux／Windows 仍按后续集中验收执行。

图片解码基础：`TerminalImageDecodeTest` 5/5、`TerminalCpuImageDecoderTest` 3/3 通过。先检查尺寸与乘法上限、PNG 分块／CRC／结束边界，RGB 补 alpha，RGBA 复用不可变像素；显式租约最后关闭时同时清掉数组引用并退还预算。PNG adapter 在后台调用内创建、使用和关闭原生对象，预留 encoded copy、codec 像素、raster surface、可变 readback 与返回数组的保守峰值；解码失败和大小不一致释放工作预算。固定本地生成的 RGBA／索引透明色／16-bit／Adam7 样本验证实际像素，多 worker 验证原生对象不跨 owner；fixture 生成一致性检查通过。此时尚未向 PTY 声明图形协议支持，store、帧寿命、压缩与绘制预算仍需后续集成验证。

实际测试发现 `scoop.graphics.Image.decode()` 接受不完整 PNG 像素。已在独立分支 `codex/strict-image-decode` 修复并合并 [Scoop PR #226](https://github.com/scoop-lang/scoop/pull/226)：只接受 `SkCodec::kSuccess`，保留颜色／alpha 和 EXIF 方向。上游新增解码 3 项及原绘图 7 项通过，本地 main 已更新并回合并修复分支推送；开发 sysroot 完整更新后，组件的同组坏图回归通过。未下载外部依赖；PR 临时文件已清理。

分块／压缩：`TerminalImageTransferTest` 6/6，连同前述核心解码 5 项共 11/11 通过。Base64 复用工具链库，逐块限制 4096 字节及非末块对齐／padding，并累计整次编码长度；空块不积累元数据，取消或任一块失败回收全部页。Zlib 复用工具链增量 decoder，固定 8 KiB 输入／输出缓冲，配置解压上限，严格拒绝截断、尾随字节、串联流和声明长度不符。测试覆盖跨输入和输出页、空流、小输入膨胀、工作预算以及最终合并时新旧数组共存的峰值，失败后已有像素租约保留。没有下载或临时文件；此变更提供传输原语，APC 协议接入仍在后续步骤。

Sixel 像素基础：`TerminalSixelDecodeTest` 6/6、`TerminalSixelPaletteTest` 3/3、`TerminalIndexedImageTest` 4/4。增量处理六位像素、重复、回车／换带、透明或寄存器零背景、声明尺寸下界及实际绘制扩展、DEC 宏和 raster 像素比例；RGB／HLS 使用版本化颜色表。像素采用 64×64 索引块，空背景保持稀疏，局部擦除只复制相交块，旧快照保留原块／原颜色。测试覆盖跨参数边界、非法输入／取消／分配失败、共享块预算，以及两个实际线程的 200 个独立版本和重复关闭后的完整回收。绘制工作量另限 67108864 次像素写入，避免反复覆盖绕过面积限制。参考固定的 xterm `graphics_sixel.c` v1.66（2026-06-28）和 `graphics.c` v1.142（2026-10-11）核对游标算法并记录换带触达范围；尚未完成真实窗口对照。DCS、VT 滚动、协议查询和绘制尚未接入，因此仍不宣告图形能力。本轮没有下载或自建临时文件；协议参考文件继续用于后续集成。

图片快照：`TerminalImageReadingTest` 4/4，原 `SnapshotTest` 5/5、`LiteralSearchTest` 7/7。`reading.images` 提供不可变资源／placement 视图，`TerminalImageLease` 支持独立帧交付所有权；显式快照自动保留图片，上传像素另有独立租约。资源、palette、索引块与元数据全部包含在 CPU 配额内，快照池另对保留内容作保守估算。失败的快照／图片表分配退还本次租约；双线程重复获取／关闭后完整回收。搜索使用共享行数据的文本投影，投影没有指向完整 reading 的反向引用：关闭原快照后 CPU 图片预算归零，搜索仍能返回正确命中。生产 model／view 的租约交接随后接入，本轮尚不启用协议能力。无下载或临时文件。

## 后续执行约束

外部依赖优先使用本地 `~/repos/scoop-dep`；需要下载时使用 `https_proxy=http://192.168.2.106:10809`。Linux 通过 `ssh nuc12`，在 `~/repos/` 创建本任务目录，依赖目录 `~/repos/scoop-deps`。Windows 通过 `/usr/bin/ssh 192.168.2.67`，在 `E:` 创建本任务目录，依赖目录 `E:/scoop-dep`。

如实际遇到编译器/底层库缺口，先在该仓库独立分支修复、验证、提交、推送、开 PR 并合并，再更新本地 main、合并回相应工作分支并更新工具链。临时文件只在仍用于后续工作时保留；阶段结束清理不再需要的文件。

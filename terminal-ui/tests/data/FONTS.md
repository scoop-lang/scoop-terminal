# 测试字体

`FiraCode-Regular.ttf` 原样取自 [Fira Code 6.2](https://github.com/tonsky/FiraCode/releases/tag/6.2) 的 `Fira_Code_v6.2.zip`，用于连字、逐列 caret 和缓存生命周期的离屏测试。SIL Open Font License 1.1，版权与完整条款见 [FiraCode-LICENSE.txt](FiraCode-LICENSE.txt)。

字体 SHA-256：`5992ab9640e2df491b2f609467b1de60e8bc39b2c28db184342a0592d98f6117`。测试显式登记字体并关闭系统 fallback，不依赖宿主安装的字体版本。

以下两项原样复用本地 Scoop 测试资料，其来源是 Skia revision `f326a1e25fc736704063922b9ce76b527b1c5efe` 的 `resources/fonts/`：

- `Roboto-Regular.ttf`：用于总宽相同但内部 caret 不等宽的退回测试。Copyright 2011 Google Inc.，Apache License 2.0，完整条款见 [Roboto-LICENSE.txt](Roboto-LICENSE.txt)。SHA-256：`466989fd178ca6ed13641893b7003e5d6ec36e42c2a816dee71f87b775ea097f`。
- `NotoSansCJK-VF-subset.otf.ttc`：仅含“是”的 CJK 子集，用于真实缺字 fallback 与双宽格绘制。Copyright 2014–2021 Adobe，Reserved Font Name “Source”，OFL 1.1，完整条款见 [Noto-LICENSE.txt](Noto-LICENSE.txt)。SHA-256：`e7f71fc8aec139bb21cc541067eabb162b87aeeac0ccfcb3c835a20d0cee340a`。

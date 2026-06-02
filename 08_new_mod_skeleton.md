# 08 · 从零搭建一个新 Mod（最小可用骨架）

> 目标：一个能进游戏、不崩溃、中文正确显示的最小 mod，作为任何新项目的起点。

---

## 1. 目录结构
```
<游戏>/mods/
└── MyMod/
    └── MyMod.mpq/                 ← 文件夹（非压缩包）
        ├── modinfo.json           ← 必须
        └── data/
            ├── global/
            │   ├── dataversionbuild.txt   ← 当前游戏版本号
            │   └── ui/layouts/            ← UI 面板 JSON
            ├── hd/ui/fonts/               ← 字体（可选）
            └── local/lng/strings/         ← 字符串 JSON（文件名任意）
```

## 2. modinfo.json（必须）
```json
{ "name": "MyMod", "savepath": "MyMod/" }
```
- `name` 必须与目录名 `MyMod/` 和 `MyMod.mpq/` 一致。
- `savepath` 保持最简（国服对此文件有额外限制）。

## 3. dataversionbuild.txt
单行版本号，**必须与当前游戏版本一致**（不符会弹"版本不匹配"或卡读取）。从已有 mod 的同名文件抄当前值。

## 4. 启动
```
"Diablo II Resurrected.exe" -mod MyMod -txt
```
- `-mod MyMod` 加载 `mods/MyMod/`。
- `-txt` 允许读 `data/global/excel/*.txt`（不改 excel 可省）。
- 国服一般通过 bn 客户端带参数拉起。
- ⚠️ 改完 json **完全重启客户端**（字符串加载时缓存）。

## 5. 字符串 JSON
`data/local/lng/strings/mymod.json`：
```json
[
  { "id": 30051, "Key": "mymod_title", "enUS": "My Dictionary",
    "zhCN": "词典", "sgCN": "词典", "bnCN": "词典" }
]
```
- **三字段同步** `zhCN=sgCN=bnCN`（国服读 bnCN，国际读 zhCN）。
- 主索引表（item-names 等）`id` 必须**数字**且唯一；自定义条目用 vanilla 最大值之上的高位段（缺 id→启动~20s 崩溃，见 `06`）。
- 文件名任意，引擎加载 `strings/` 下所有 `.json`，**后加载覆盖同名 key**。
- 面板里引用：`"textString": "@mymod_title"`。
- ⚠️ 不要用 Python 直接读写 `ui.json`/`bnet.json`（含裸控制字符易损坏）。

## 6. 面板自动注册（无需登记）
引擎**自动扫描** `layouts/` 下所有 `*hd.json`，按根节点 `name` 注册到 PanelManager。**不需要**在 `_profilehd.json` 或任何地方手动注册（详见 `07` §2）。只需：
1. 文件在 `layouts/` 目录；2. 文件名以 `hd.json` 结尾；3. 根 `name` 与 `PanelManager:TogglePanel:<name>` 一致。

## 7. 字体（可选）
要用自定义图标/特殊符号，把合并好图标的中文字体放到 `data/hd/ui/fonts/...`（机制见 `04` §4）。用符号前先查字体覆盖。

## 8. 不可触碰（防闪退，详见 06）
- `data/hd/character/**/*.model`（启动崩；`env/model/` 安全）
- `data/hd/character/enemy/*hire.json`（结构禁止）
- `texture_desc_cache.json`（4+ 分钟加载）
- 引用被国服和谐的资产（骨甲/骷髅祭坛）→ DeviceLost
- `ui.json`/`bnet.json` 用 Python 直接解析

## 9. 验证清单
- [ ] 正常启动、不卡读取条、无 DeviceLost
- [ ] 自定义中文不乱码、图标不是方块
- [ ] 面板能开/关
- [ ] 国服(bnCN) 与国际(zhCN) 文字一致

---

## 10. 进阶：自定义面板/词典系统 设计要点
（详见 `07`，这里给搭建顺序）
1. 新建 `MyMod_MiniButtonshd.json`（`TooltipsPanel`，priority 99）放一个 Toggle 按钮 → `TogglePanel:MyMod_Panel`。
2. 新建 `MyMod_Panelhd.json`（`SettingsPanel`）：显式 `RectangleWidget` 背景（不用 fitToParent）+ Close 按钮（`ClosePanel:MyMod_Panel`）+ TabBar（children=Tab 内容面板）。
3. 内容用脚本生成填进 TableWidget。
4. 设计原则：单文件单面板；面板开关用 `PanelManager` 消息（不用 TimerWidget 控流）；多步切换用 CALL 模式；颜色在 layout 里用 `fontColor` style（不是 `ÿc`）。

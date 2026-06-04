# 07 · UI 布局 · 面板 · 覆盖特效

> D2R 的 HD 界面由 `data/global/ui/layouts/*.json` 数据驱动。本篇是 UI 层实战手册，来自 MDK/Comg/yupgoolg/SU 源码逐条验证。

---

## 1. 解析 D2R JSON（JSONC）

D2R 的 JSON 是宽松 JSONC（含 `//` `/* */` 注释、尾逗号），Python 标准库不接受：
```python
import re, json
def load_d2r_json(path):
    with open(path, encoding='utf-8-sig') as f:   # 处理 BOM
        raw = f.read()
    raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
    raw = re.sub(r'//[^\n]*', '', raw)
    raw = re.sub(r',(\s*[}\]])', r'\1', raw)
    return json.loads(raw)
```
> ⚠️ `bnet.json`/`ui.json` 含裸控制字符，正则去注释可能破坏内容——仅用于分析，生产写入要谨慎。字符串内含 `//` 也会被误伤。

---

## 2. 面板注册真相（纠正常见误解）

> 🛑 **误解**：很多资料说"`_profilehd.json` 是面板注册表，要在里面登记面板→布局文件映射"。**这是错的**（经 MDK/Comg 实测纠正）。

**真相**：
- 引擎**自动扫描** `layouts/` 目录所有 JSON，**文件名（去掉 `hd.json` 后缀）= 面板名**。无需注册。
  - `SU_DictPanelhd.json` → 面板名 `SU_DictPanel` → `PanelManager:TogglePanel:SU_DictPanel`
- `_profilehd.json` 是**全局命名变量定义文件**（坐标/颜色/字号/字符串/文件名等 `$变量`），不是注册表。面板文件用 `$变量名` 引用它。
- ⚠️ 改 `_profilehd.json` **只追加新变量，不改已有**（破坏依赖该变量的其他面板）。

---

## 3. 坐标系与锚点

```
屏幕原点(0,0)=左上角
anchor{x:0.5,y:1} = 水平居中+底部对齐
rect.x/y = 相对锚点偏移（正=右/下）
子 Widget 坐标 = 相对父 Widget 左上角
```
| anchor | 位置 | 典型用途 |
| --- | --- | --- |
| `{x:0.5,y:1}` | 底部居中 | MiniButtons HUD |
| `{x:1,y:0}` | 右上角 | HUD 警告 |
| `{x:0,y:0}` | 左上角 | 固定面板 |

> ⚠️ **勿用负坐标把面板推出屏外来"隐藏"**（如 `rect.x:-1394`）——会导致引擎仍拉起但不可见、功能锁死。用 `TogglePanel` 开关。

---

## 4. 消息路由（已验证）
```
PanelManager:OpenPanel:Name      打开
PanelManager:ClosePanel:Name     关闭
PanelManager:TogglePanel:Name    切换（HUD按钮首选）
ClosePanel:Name                  面板内 Close 按钮（省略 PanelManager 前缀）
SettingsPanelMessage:CheckChanges:SubPanel     Tab 切换（主流）
SettingsPanelMessage:ToggleChildPanel:SubPanel Tab 切换（直接开关子面板）
ModalMessage:Confirm:https://...               弹确认框→开外部链接
```
**CALL 文件跳转模式**（关 A + 开 B，比裸 TimerWidget 可靠）：建一个自关闭的中转 `Panel`，内放几个 TimerWidget 依次发 Close A / Open B / Close 自身。
> ⚠️ `TimerWidget` 时序不稳，多步切换优先用 CALL 模式。

---

## 5. Widget 类型速查
| 类型 | 用途 | 关键字段 |
| --- | --- | --- |
| `Widget` | 容器 | rect, anchor |
| `ImageWidget` | 贴图 | filename, rect, scale |
| `NineTileImageWidget` | 九宫格可拉伸背景 | filename, rect |
| `ButtonWidget` | 按钮/图标/热区 | filename, onClickMessage, tooltipString, hoveredFrame, pressedFrame, tooltipOffset |
| `TextBoxWidget` | 文本 | text/textString, pointSize, style, fitToText |
| `RectangleWidget` | 色块/遮罩 | color[R,G,B,A], borderColor, fitToScreen |
| `ClickCatcherWidget` | 拦截穿透点击 | fitToParent |
| `FocusableWidget` | tooltip 接收器(无视觉) | fitToParent, tooltipString, tooltipStyle |
| `TabBarWidget` | 选项卡 | textStrings, tabMessages, filename（children 必须空）|
| `ScrollViewWidget`/`ScrollControllerWidget` | 滚动 | fitToParent, viewName/scrollControllerName |
| `TableWidget`/`TableRowWidget` | 表格 | columns(width+alignment), rowHeight |
| `TimerWidget` | 定时发消息 | time(秒), message（时序不稳）|

## 6. Panel 类型 + tooltipString 有效性
| Panel | priority | tooltipString | 用途 |
| --- | --- | --- | --- |
| `TooltipsPanel` | 99 | ✅ | HUD 常驻按钮(MiniButtons) |
| `HelpPanel` | 300 | ✅ | F1 帮助，预渲染图+热区 |
| `SettingsPanel` | 6 / 9002 | ✅ | 自定义面板主体 |
| `VideoOptionsPanel` | 9003 | ✅ | Tab 内容面板 |
| `PlayerInventoryPanel` | — | ❌ | 物品栏，引擎限制 tooltip 无效 |
| `Panel` | — | — | CALL 中转，自关闭 |

priority：HUD 按钮 99；侧边面板 5-10；全屏主体 9002；Tab 内容 9003（高于主体才可见）；全屏+遮罩 100。

---

## 7. 信息展示方式
- **静态文本** TextBoxWidget（`text` 写死 / `textString:"@key"` 取字符串表）。
- **表格** TableWidget + ScrollView（词典/配方）。columns 定义列宽，每 TableRowWidget 的 children 按序映射列。
- **tooltip**：ButtonWidget 直接挂 `tooltipString`（有点击反应，加 `pressedFrame:0` 去反馈）；或 TextBox 内嵌 `FocusableWidget(fitToParent)` 实现"文字可见+hover提示，无点击"。
- **Mini 按钮**：`TooltipsPanel(priority:99)` + ButtonWidget，`onClickMessage: TogglePanel:目标`，HUD 常驻。
- **自包含全屏面板**（避坑）：根 `SettingsPanel` → 显式 rect 的 `ContentArea` Widget → `ScrollView(fitToParent)` → `TableWidget`。
  - ❌ 别让 SettingsPanel + ScrollView 都 `fitToParent` → 内容溢出到屏幕(0,0)。给 ScrollView 一个显式 rect 父容器。
  - ❌ 别把 `VideoOptionsPanel` 当无定位子节点内联 → 塌成 0×0 不可见。要么独立文件，要么直接用 ScrollView+Table。

---

## 8. 颜色码在 layout 里的陷阱（重要）
- **`ÿc9`/`@cyc9` 颜色码只在"物品/NPC 字符串值"处解析；在 layout JSON 的 TextBox `text` 里不解析**，会原样显示字面 "ÿc9"。
- layout 里要上色必须用 style 的 `fontColor`（如 `"fontColor": "$FontColorGoldYellow"`）。
- 在字符串文件(item-names 等)里用 `ÿc`（`chr(0xFF)+'c9'`）；在 layout/profile 变量里用 `@cyc`。
- **可上色的字符串值范围广**：除物品名外，**怪物暗金词缀名也能上色**——它们在 `bnet.json`（如 `uniquecursed`=诅咒、`monsteruniqueprop6`=石肤术、各 `monsteruniqueprop*`），改 `zhCN/sgCN/bnCN` 加 `ÿc` 前缀即变色强调危险词缀。`bnet.json` 含裸控制字符 → **只文本替换、禁 json 解析**；三字段同步。
- 🔴 **字号无法用字符串改**：`ÿc` 只能控制**文字内容 + 颜色**，**没有"字号/放大"码**。要更大的字只能在渲染它的 UI layout 里调（怪物悬浮名由引擎渲染，改不了）。想强调又放不大 → 用**颜色 + 醒目符号**（`◆`/`★` 等字体安全符号，前后包夹）替代。

---

## 9. 背景（防透明穿透）
- **模式A 显式 rect**：`RectangleWidget` 带 rect + `color:[R,G,B,A]`（侧边面板推荐）。
- **模式B 背景图**：`ImageWidget filename`。
- **模式C 全屏遮罩**：`RectangleWidget fitToScreen:true` + `color:[0,0,0,0.7]` + 内嵌 `ClickCatcherWidget(fitToParent)`（全屏面板，挡点击穿透）。
- ❌ 别在 RectangleWidget 上用 `fitToParent`，某些 Panel 下失效显示透明。

---

## 10. Sprite 贴图
```
JSON 引用: "filename": "PANEL/BTN/btn_j_0"   （无扩展名，大小写不敏感）
实际文件:  data/hd/global/ui/panel/BTN/btn_j_0.sprite
必须同时有: 同名 .lowend.sprite（低画质模式必需，缺了报错）
```
帧控制：`hoveredFrame`/`pressedFrame`/`disabledFrame`。Mini 按钮贴图通常 4 帧。`blank` = 全透明（HelpPanel 热区用）。

---

## 11. 字体与图标内嵌
- D2R 多字体 fallback 链：中文主字体 → 图标字体(kodia 等) → 西文字体。找到字符即停。
- **字符串里内嵌图标**：直接插入对应 Unicode 码点字符，引擎从字体取图标字形。如 `"ÿcT<F05A>ÿc4..."`（F05A=任务物品图标）。
- 图标常见区：Blizzard PUA（E001-F7EC，装备类型/手柄键图标）、kodia 物品图标（F020-F07D）、合并进中文字体的 loot-filter 图标（散布多个 Unicode 区，靠字形宽度=UPM 判别）。
- ⚠️ 用任何特殊符号/图标前**必须查字体覆盖**，否则空白方块（见 `04`）。

---

## 12. 覆盖特效（Overlay / VFX 注入）
通过向实体 JSON 的 `entities`/`components` 注入组件实现，**不替换整文件**：
- **掉落光柱**（高价值物品地面光束）：改 `data/hd/objects/items/runes/*.json` 等，注入 `VfxDefinitionComponent`（指向光柱 .particles）+ `TransformDefinitionComponent`（y 偏移浮于物品上方）。
- **Boss 发光/头顶符文**：改 `data/hd/character/enemy/<boss>.json`，注入 VfxDefinition + Transform（如 `position.y:7.0`）。
- **头顶名字/昵称**（NPC/敌人/佣兵悬浮名）：往角色实体 json（`character/{npc,enemy}/<name>.json`）的 `entities[]` **追加一个实体**：
  ```json
  { "type":"Entity","name":"entity_root","id":<唯一>,"components":[
    {"type":"VfxDefinitionComponent","filename":"data/hd/nickname/particles/<name>.particles","hardKillOnDestroy":false},
    {"type":"TransformDefinitionComponent","position":{"x":0,"y":9.0,"z":0}} ]}   // y=头顶高度，boss 用 13
  ```
  - **名字是预渲染贴图**：`.particles` 引用 `nickname/textures/graphic/npcname_<x>.texture`（+`..glow`）。所以名字是**图片**——换文字/中文化要重做贴图，改不了字符串。
  - **国服安全**：这类只 ship `.json`+`.particles`+`.texture`、**无 `.model`** → 无崩溃机制（见 `06` 已纠正的佣兵/角色实体误判）。佣兵 `*hire.json` 实体同理可加（真正禁的是 `.model` 与 `excel/act*hire.json`）。
- **地面信标/传送标记**：`data/hd/env/porory/beacon/` Prefab + 注入到 `env/preset/`、`roomtiles/`。
- **路径箭头**：方向箭头 .particles 注入场景 preset tile。
> ⚠️ 引用被国服和谐的资产路径（骨甲/骷髅祭坛）会 DeviceLost 崩溃，见 `06`。

---

## 13. 多 mod 兼容核心原则：程序化注入，不整文件覆盖
**问题"修一个坏一个"**：多个 mod 各自覆盖同一个 `hudpanelhd.json`/`_profilehd.json` → **最后拷贝的赢，其余被完全抹掉**。

**正解（D2RMM/编译式做法）**：不预置改好的整文件，而是**构建时**载入原版文件 → 按 name 定位 → 程序化注入新 widget（先查重防重复插入）→ 序列化输出。
```js
// D2RMM 思路
const hud = D2RMM.readJson('global\\ui\\layouts\\hudpanelhd.json');
if (!hud.children.some(c => c.name === 'my_btn'))
    hud.children.push({ type:'ButtonWidget', name:'my_btn', fields:{...} });
D2RMM.writeJson('global\\ui\\layouts\\hudpanelhd.json', hud);
```
- 同理 `_profilehd.json` 只**追加**变量、`item-names.json` 只**改命中条目**，多 mod 才能共存。
- 手柄模式读 `layouts/controller/`，键鼠 HUD 的注入在手柄下不生效，需单独注入。

---

## 14. 可滚动「图标+表格」词典面板标准（Tab 壳 + 子面板）

> 自建词典/配方面板（方块配方、符文之语等）的完整可渲染标准。来自 D2R 原生 `itemdictionarycuberunegempanelhd`/`itemdictionaryrunewordpanelcn*` 逐字段实证（2026-06）。**踩过的坑都在这。**

### 14.1 🔴 铁律：TableWidget 内容行的 `name` 必须用引擎识别值，否则整行不渲染

D2R 的 `TableWidget`（在 `SettingsPanel`/`VideoOptionsPanel` 内）**只渲染 `name` 被引擎识别的 `TableRowWidget`**。这是最大的坑：结构、坐标、贴图全对，但行 `name` 自创 → **该行完全不显示**（连文字都没有），且**不报错**。

| 行用途 | **必须**的 `name` |
| --- | --- |
| 章节标题行（带分隔线） | `"Row Gameplay Options"` |
| 内容行（图标/文字/配方） | `"Row ItemNameDisplayMode"` |
| 说明/注释行 | `"Row CubeRecipeDescription"` / `"Row RunewordDescription"` |

> 实测：自创 `name:"Row CubeRecipe"` → 表格只显示标题行，所有配方行空白。改成 `"Row ItemNameDisplayMode"` 后立即全部渲染。**别自创行名。**

### 14.2 面板外壳（VideoOptionsPanel + 原生滚动）

```
VideoOptionsPanel {priority:9003, rect:"$OptionsPanelRect", anchor:{x:0.5}, applySettingsImmediately:false}
 ├ ImageWidget "ScrollBarBackground" {rect:"$OptionsScrollBarBackgroundRect", anchor:{x:1.0}, filename:"PauseMenu\\VerticalScroll"}
 │   └ ScrollControllerWidget "ScrollController" {rect:"$OptionsScrollBarRect", viewName:"ScrollView", 上/下箭头/bar filepath}
 └ ScrollViewWidget "ScrollView" {fitToParent:true, scrollControllerName:"ScrollController"}
     └ TableWidget "OptionsTable" {columns:[{width,alignment:{h:fit,v:fit}}...], rowHeight:"$OptionsTableRowHeight"(=100)}
         └ TableRowWidget...（见 14.1）
```
- `rowHeight` 用 `$OptionsTableRowHeight`(=100) 即可，**不要自己塞 0/变量未定义**；行高有效后内容才不被裁。**内容坐标全部 ≤ 行高**（图标 y≈48-54、分隔 y≈58）。
- 列按 `TableRowWidget.children` **顺序映射**：children[0]→列1，[1]→列2…

### 14.3 行内 widget（图标/文字/分隔）

一个内容行 = `TableRow "Row ItemNameDisplayMode"` → 每列一个 `Widget` 容器 → 内部 widget 用**绝对 rect{x,y}** 摆放（原生就是这么干，可靠）：
- **物品图标**：`ButtonWidget {rect:{x,y,scale}, filename:"items/misc/gem/ruby"|"items/misc/rune/el_rune"|"items/armor/boot/...", tooltipString:名/@token, pressedFrame:0}`
  - `scale` 调图标大小（原生 0.75；嫌大用 0.6 左右）。**`scale` 写在 `rect` 内**：`rect:{x,y,scale:0.62}`（合法，原生分隔符就这么用）。
  - 物品图标路径怪癖：普通宝石是裸名 `gem/ruby`（**非** `normal_ruby`）；蓝宝石 `saphire`（拼写）。
- **文字**：`TextBoxWidget {fitToText:true, rect:{x,y}, text, style}`。
- **分隔符**：`ImageWidget {rect:{x,y,scale:0.6}, filename:"itemDictionary/cubehelp_plus"|"cubehelp_equal"}`。
- **混排防重叠**：图标宽度固定、文字宽度可变。用**流式 x 光标**按每项真实宽度推进（CJK≈30px/字、图标≈缩放后宽），别用固定槽位——否则长文字压住后面的图标（实测过）。

### 14.4 文字上色（按品质）

- ⚠️ `ÿc` 颜色码在 layout 的 TextBox `text` 里**不解析**（见 §8）。上色只能靠 `style` 的 `fontColor`。
- 做法：往 `_profilehd.json` **追加**带色样式（只追加新 key）：
  ```json
  "StyleCubeGold": { "fontColor": "$FontColorGoldYellow", "pointSize": "$MediumFontSize", "alignment": {"h":"left","v":"center"} }
  ```
- 品质色参考引擎自带：暗金/任务=`$FontColorGoldYellow`，稀有=`$FontColorYellow`，魔法=`$FontColorBlue`，套装=`$FontColorGreen`，手工=`$FontColorOrange`。

### 14.5 Tab 壳主面板

```
SettingsPanel {priority:9002, fitToParent:true}
 ├ RectangleWidget "Background" {fitToScreen, color:[0,0,0,0.7]} → ClickCatcher + Anchor(背景图 FrontEndOptionsBG + Title + CloseButton)
 ├ ImageWidget "SettingsBackground" {rect:"$SettingsPanelBackgroundRect", filename:"Controller/Panel/Options/Panel_Options_BG"}
 └ TabBarWidget "OptionsTabs" {tabCount:N, textStrings:[...], tabMessages:["SettingsPanelMessage:CheckChanges:<子面板名>"...], filename:"Controller/Panel/Stash/V2/StashTabs"}
```
- 子面板**靠文件名自动注册**（`su_xxxhd.json` → 面板名 `SU_Xxx`，无需登记，见 §2）；`tabMessages` 指向子面板名即可切换。`SettingsPanelMessage:CheckChanges` **能切到 `VideoOptionsPanel` 子面板**（实证）。
- ⚠️ **别照抄原版主面板的 `CenterSection`**——它带 `$DictionaryModCreditText`（"Created by..."版权字，显示在屏幕左侧），抄进来就会一直显示。自建主面板不要这个节点。

### 14.6 排查"面板能开但内容空白"
1. 内容行 `name` 是不是 `"Row ItemNameDisplayMode"`（**最常见**，见 14.1）。
2. 行高是否有效（`$OptionsTableRowHeight`），内容 y 是否 ≤ 行高。
3. 图标 `filename` 路径是否存在（普通宝石裸名、`saphire` 拼写）。
4. 子面板是否被 `tabMessages` 正确指向、文件名→面板名是否对。

### 14.7 词典面板"重建/翻译"实战要点（脚本化改造词典时）

改造现成词典面板（如把符文之语的符文构成从文字换成图标、把英文属性翻成中文）时踩过的坑：

- **构成用图标**：面板里常把"由哪些符文/宝石构成"写成 `@rNNL + @rNNL` 文字（`@rNN`=符文序号 1-33，El=1…Zod=33）。换成图标：解析出序号 → `ButtonWidget{filename:"items/misc/rune/<code>_rune", rect:{x,y,scale}}`，比文字清晰得多。`scale` 别太小（0.6 几乎看不清，**0.9~1.0** 才够大）。
- 🔴 **tooltip 换行是真换行符**：`tooltipString` 里的换行在 JSON 文件中写作 `\n`（**JSON 转义的换行符**，解析后是 0x0A）。脚本处理时若把它 `join` 成字面两字符 `\n`（如 Python 的 `'\\n'.join(...)`），游戏里会**原样显示 "\n" 文字、完全不换行**。务必用真换行符 `'\n'.join(...)`，`json.dump` 会自动转义回去。
- 🔴 **生成器要幂等：从不可变备份读，别从自己的输出读**。"读原面板→抽数据→重建→写回原文件"的脚本，第二次跑会读到**已重建**的文件（@rNN 文字已变成图标、数据丢失）→产出残缺。**先把原始文件备份到独立目录，脚本永远从备份抽数据**，写回工作目录。
- **`@token` 前缀别拼字符串**：要在引擎本地化名（`@RunewordNN`/`@gpb` 等）前加标记（如 ★），**别拼成 `"★@RunewordNN"`**（有破坏 token 解析的风险）。用**独立的 TextBox** 放 ★，名字 TextBox 仍是干净的 `"@RunewordNN"`。
- **英文属性→中文：短语映射 + 长度降序匹配**。D2 属性高度公式化，用"英文短语→中文"替换表即可覆盖绝大多数（数值/范围原样保留）。**关键：按短语长度降序匹配**，否则短词抢匹配（`Defense` 会先吃掉 `Defense vs. Missile`、`Resist` 吃掉 `Resist Fire`）。技能名需单独维护一张表（D2 技能多，约 80+）。先翻结构短语（`Aura When Equipped`/`when you Kill an Enemy`/`(Necromancer Only)`），再翻技能名，迭代看残留逐步补表。

---

## 15. 🔴 整文件覆盖核心面板 = "版本固化"陷阱（DLC/补丁后必坏）

> 与 §13"程序化注入"同源，但针对**引擎核心面板**（赫拉迪姆方块、库存、技能树等）单独强调，因为坑得最惨。

**现象**：mod 里放了一份某核心面板的整文件覆盖（如 `horadriccubelayouthd.json`），当时是照着**那个版本**的游戏改的。游戏出 DLC/大版本后，官方更新了该面板（新背景、新布局、新尺寸），但你的覆盖文件还停在旧快照 → 游戏加载你的旧版 → **错位 / 纯透明 / 缺背景 / 用了已不存在的 sprite**。玩家看到的就是"DLC 之前的样子"。

**根因**：mod 文件**覆盖**同名基础文件；只要文件在，引擎永远用你的、不用基础游戏的当前版本。

**正解**：
- **不需要定制的核心面板，根本别 ship 覆盖文件**。缺失 = 引擎回退基础游戏**当前版本**资产（自动跟随 DLC/补丁）。
- 已有的旧覆盖坏了 → **直接删除该覆盖文件**（mod 内），即可回退到正确的当前版本。删前备份。
- 实证：JCY 不覆盖 `horadriccubelayouthd.json`（盒子主页交给基础游戏渲染正确 DLC 版），只**另起新文件**加一个 mini 盒子面板（`HoradricCubePanel` 不同 `name`、高 priority、独立 rect）。SUMOD 曾 ship 旧版 `horadriccubelayouthd.json` → DLC 后透明错乱；删掉即恢复。

**要在核心面板上加东西怎么办**：别改原文件，**新建独立面板文件**（自定义 `name`，靠文件名自动注册，见 §2），用 HUD 按钮 `TogglePanel:<你的面板>` 或定时器打开它。这样既不固化基础面板版本，又能加功能（mini 盒子/快捷面板就是这么做的）。

> 同理适用于任何"当时照抄一份改"的基础 layout：能注入/另起就别整文件覆盖，否则就是给未来的版本更新埋雷。

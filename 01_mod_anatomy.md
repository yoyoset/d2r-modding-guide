# 01 · Mod 全景图（看懂一个 D2R mod 的全部内容）

> 目标：拿到任意 D2R mod，知道**它的内容由哪些文件定义**、**按什么顺序读能最快看懂**、**客户的需求该落到哪一层**。

---

## 0. 一个 D2R mod 的物理形态

- mod 位于 `<游戏>/mods/<名字>/<名字>.mpq/`。
- ⚠️ 注意：`<名字>.mpq` 通常是**文件夹**（不是打包档案），里面是松散文件。
- 用启动参数 `-mod <名字> -txt` 让客户端直接读这个文件夹里的松散 json/txt。
- **改完不需要重新打包**：改 json → **完全重启客户端**（字符串在加载时缓存，重进游戏不够）→ 生效。
- `modinfo.json`（根部）：mod 身份与存档路径。

---

## 1. Mod 内容的三层结构

任何 D2R mod 的内容都落在这三层。看懂这三层 = 看懂整个 mod。

### 第一层：文本层 `data/local/lng/strings/*.json`（mod 主体）
所有"文字"。多数 mod 的内容主体在这里。

| 文件 | 管什么 |
| --- | --- |
| `item-names.json` | 物品/宝石/符文名 + loot 掉落简称 |
| `item-modifiers.json` | 装备属性描述（tooltip 每一行） |
| `item-nameaffixes.json` | 词缀名、品质名 |
| `item-runes.json` | 符文名 |
| `item-gems.json` | 宝石镶嵌效果文字 |
| `bnet.json` | **品质标签 + 部分宝石名（CN 端会抢显示，优先级高）** |
| `skills.json` | 技能名/描述 |
| `levels.json` | 地图/区域名 |
| `ui.json` | 界面文字、按钮、悬浮提示 |
| `monsters.json` 等 | 怪物名等（按 mod 而定） |

### 第二层：UI 层 `data/global/ui/layouts/*.json`
所有"界面/交互"：HUD、面板、按钮、消息路由。

| 关键文件 | 作用 |
| --- | --- |
| `_profilehd.json` | **面板注册总表** —— 先读它，知道 mod 有哪些自定义面板 |
| `hudpanelhd.json` | 主底栏 HUD（技能栏、菜单、自定义按钮注入点） |
| `hudwarningshd.json` | 右上角警告面板（**区域名 InfoText + 装备损坏 DurabilityWarning 的父容器**） |
| `horadriccubelayouthd.json` | 原版赫拉迪姆方块面板 |
| `itemdictionary*hd.json` | 方块百科配方面板（一大组） |
| `controller/` | 手柄模式专属布局（键鼠改动在此**不生效**，需单独处理） |

### 第三层：美术层 `data/hd/`
所有"外观"：字体、贴图、特效、音效。

| 子目录 | 内容 |
| --- | --- |
| `data/hd/ui/fonts/*.ttf` | 字体（loot 简称里的特殊符号/图标靠它，常为合并图标的定制字体） |
| `data/hd/items/*.json` | 物品外观/掉落贴图配置 |
| `data/hd/global/sprites` | 2D 贴图精灵 |
| `data/hd/overlays` / `env` | 技能特效 / 场景 |
| `data/hd/global/sfx` | 音效 |

### （第四层）逻辑层 `data/global/excel/*.txt` —— 数值与规则
武器/防具/技能/符文之语/方块配方/掉落/怪物数值等。

> ⚠️ **很多文本/UI 类 mod 根本不碰这层**（不改平衡性）。注意：excel 在 `-mod` 模式**国服在线可用、不会闪退**，但改**数值/平衡 = TOS 封号风险**（见 `06`）。真正的国服崩溃来自引用被和谐的美术资产，不是 excel。

---

## 2. 读取顺序（最快看懂一个 mod）

```
1. modinfo.json                  → mod 身份/存档路径
2. _profilehd.json               → 有哪些自定义 UI 面板（全局地图）
3. strings/ 全部 json            → 改了哪些文字（mod 内容主体）
4. ui/layouts/ 关键面板          → 改了哪些界面/交互
5. hd/ui/fonts + hd/items        → 改了哪些外观
6. excel/*.txt（若有）           → 是否改了数值逻辑
7. diff vs 原版基准(CASC/社区基准库) → 精确知道"相对原版改了什么"
```

> **单看文件 = 知道内容；diff 原版 = 知道改动。** 要真正理解 mod"做了什么"，第 7 步不可省。

---

## 3. 客户需求 → 该改哪一层

| 客户要什么 | 落到哪 | 注意 |
| --- | --- | --- |
| 改名 / 翻译 / 去和谐 / loot 简称 | 文本层 strings | 注意 bnet.json 抢显示；三字段同步 |
| 装备描述配色 / 重点高亮 | item-modifiers.json | 区分魔法属性行 vs 结构行 |
| 改面板 / HUD / 百科 / 加按钮 | UI 层 + 字体 | 手柄模式要单独处理；改坐标勿推出屏外 |
| 物品图标 / 颜色 / 掉落特效 | hd/items + sprites + 字体 | 动贴图在 CN 端有风险 |
| 改数值 / 平衡 / 新符文之语 / 新物品 | excel/*.txt | ⚠️ 在线可用但**改平衡=TOS 封号风险**；勿引用被和谐的美术资产(会 DeviceLost，见 06) |

---

## 4. 接手一个 mod 的标准开场（清单）

- [ ] 读 `modinfo.json` 与 `_profilehd.json`
- [ ] 列出 `strings/` 各文件大小（大的 = 改动重点）
- [ ] 扫 `ui/layouts/` 文件名（认出自定义面板 = 非原版名）
- [ ] 看 `excel/` 有没有 txt（有 = 动了逻辑，警惕）
- [ ] 看 `hd/ui/fonts` 是否定制字体（决定能用哪些符号）
- [ ] 对照原版基准 diff，列出真实改动清单
- [ ] 把客户需求映射到层（见 §3），再按 `02`/`03`/`04` 动手

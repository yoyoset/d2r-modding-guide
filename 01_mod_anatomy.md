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
| 改名 / 翻译 / 去和谐 / loot 简称 | 文本层 strings | 注意 bnet.json 抢显示；简中写 zhCN（见 02） |
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

---

## 5. 资产依赖扫描与分体贴图（漏拷 = 贴图错误/粉块）

预设/粒子/roomtiles 之间靠**文本内嵌路径**互相引用。给 mod 补资产时用 BFS 递归扫描：

```
种子文件 → 正则抓 data/(hd|global)/.../*.(texture|particles|model|json|physics) →
  目标 mod 已有 → 只扫它的依赖
  来源 mod 有   → 拷贝 + 继续扫描
  都没有       → 原版 CASC 资产，跳过
```

两个实测踩过的坑（症状都是"看起来导入成功了，游戏里贴图错误"）：

1. **分体贴图约定**：json/particles 里引用 `xxx.texture`，散装磁盘上实际是
   `xxx$a.texture`（alpha）+ `xxx$rgb.texture` 两个文件（部分只有 `$a`），运行时自动配对。
   依赖扫描按引用名直查 `exists(xxx.texture)` 会**全部误判为"原版资产"跳过**——
   如果那批恰好是被和谐删除的资产（血迹 decal 等），就漏拷了。
   判存在性必须同时尝试 `$a`/`$rgb` 后缀。
   这个规则主要针对 `.texture`；UI `.sprite` 是独立文件，通常以 `SPa1` 头 + RGBA 像素保存，并需要同名 `.lowend.sprite` 成对携带。
2. **种子文件"已有即跳过"陷阱**：目标 mod 里已存在同名文件 ≠ 内容相同。
   如果目标里是别的 mod 的简化版（或原版），来源 mod 的加强版永远进不来。
   对明确要"以来源为准"的文件维护一个 FORCE 覆盖清单（覆盖前备份）。

安全守卫照旧：`hd/character/**/*.model|.skeleton` 永不拷（CN 闪退，见 06）。

---

## 6. 移植 D2RMM 脚本 mod（mod.js 内嵌内容）到散装 mod

D2RMM mod = `mod.json`（元数据/配置）+ `mod.js`（用 `D2RMM.readJson/writeJson/copyFile`
API 把内容写进游戏目录）。大型 mod 会把全部 JSON 载荷内嵌在 mod.js 里（几百 KB 很常见）。
不装 D2RMM 也能移植——**写个 Node 垫片仿真 API 跑一遍**：

```js
const D2RMM = {
  readJson(rel)        { /* 从目标 mod 的 data/ 读(容忍注释/尾逗号) */ },
  writeJson(rel, data) { /* 落到暂存目录，别直接进 mod */ },
  copyFile(s, d, r)    { /* 记录日志即可 */ },
};
new Function('D2RMM', 'config', 'console', fs.readFileSync('mod.js','utf8'))(D2RMM, config, console);
```

`readJson` 指向**目标 mod 现状**，merge 逻辑就会基于你的文件真实执行。产物落暂存目录后逐文件审查再装。

移植审查清单（每条都是实测踩过的）：

- **writeJson = 整文件写**。mod 自带的 `hudpanelhd.json` 等核心 layout 多半是"原版+它的按钮"
  整体替换——直接采用会冲掉目标 mod 的全部自定义 widget。**只摘它新增的 widget 注入现有文件**
  （diff 新旧 widget 树的 name 集合即可定位）。
- **字符串 json 同样是整文件覆盖**。如果 mod 写一个目标 mod 没有的字符串文件（如 `npcs.json`），
  产物只含它的新条目 → 装进去就把**原版该文件的全部字符串顶没了**（NPC 名字消失）。
  必须先从 CASC 提原版垫底再合并（CN 端简中写 zhCN，见 02）。
- **新 id 段全局碰撞检查**：扫目标 mod 全部 strings/*.json + 原版同名文件。
- **`copyFile('hd','hd',true)` 类整目录拷贝**：先看 mod 包里这个目录到底有什么、
  和目标 mod 已有资产是否冲突，别无脑整拷。
- **`@key` 引用审计**：面板里 `text`（固定行高表格）引用多行字符串会叠行；
  `tooltipString`（自动撑高）则无碍。移植前按字段统计一遍引用。

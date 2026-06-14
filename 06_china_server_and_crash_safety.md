# 06 · 国服(bnCN)兼容 · 和谐 · 防闪退完全指南

> D2R 国服(网易) mod 的核心难点都在这。本篇是 guide 最重要的实战章节，来自 JCY 源码 + blz-log 实测 + 社区(MDK/BUFF)联机验证。
> ⚠️ 含**已被纠正的错误结论**——别再踩。

---

## 1. 语言代码（locale）与 sgCN/bnCN 翻案（2026-06-13 实证修正）

> ⚠️ **本节旧版结论（"国服读 sgCN/bnCN 不读 zhCN，缺了卡读取"）已被实证推翻**，修正如下。

**国服客户端显示简中读的就是 `zhCN`。** 证据链：

1. **国服原版数据**（CASC `Data:osi` 提取）字符串文件只有标准 15 国际化字段（enUS/zhCN/zhTW/koKR/deDE/...），**根本不存在 sgCN/bnCN 字段**——客户端不可能依赖一个原版数据里没有的字段做主读取。
2. **三个在国服正常运行的参考 mod（JCY/MDK/ComG）全库 0 条 sgCN/bnCN**，其中 JCY 是国服在线长期验证的 mod。
3. **正面实测**：新建字符串 key 仅写 `enUS`+`zhCN` 即在国服正常显示（骷髅反和谐 susk* 配方，游戏内截图验证）。
4. 国服和谐（如骷髅→"石英"）是**运行时按字符串 Key 拦截**，不是数据字段层——原版 zhCN 字段里就是未和谐的"头骨宝石"。

**`sgCN`/`bnCN` 的真实身份**：SU 系 mod 自带的**防御性注入字段**（sgCN=松岗 legacy 标签、bnCN=NetEase 标签，SU 文档自述"确保任意 locale 都生效"的保险写法）。"缺了就卡读取/改动失效"从未有过 A/B 实测，是一次修复误归因后文档互相转抄形成的**回音室谬误**（与社区色码表同款失败模式）。

**现行规则**：
- **新写文件/新条目：不需要 sgCN/bnCN**，写 `zhCN`（+`enUS` 兜底）即可。
- **继承了 SU 系文件的库**（条目里已存在 sgCN/bnCN）：改 `zhCN` 时**同步改掉旧值**——客户端是否会优先读这些字段未做过冲突实测，留着陈旧值是无谓风险；同步是零成本保险。
- 卡"正在读取"的排查别再从 sgCN 开始，见 §2 模式 A。

---

## 2. 国服三大故障模式（精确归因）

国服出问题就这三种，**对症排查、别瞎猜**：

### 模式 A：卡"正在读取"（加载失败/极慢）
按概率排查：
1. `dataversionbuild.txt` 版本号与当前游戏不一致。
2. 存在 `data/hd/texture_desc_cache.json`（不应在 mod 内 → 重验所有贴图，加载 4+ 分钟）。
3. 存在 `data/hd/character/**/*.model`（**真正的硬禁 = `.model` 二进制网格**，顶点格式/和谐冲突）。
   > ⚠️ 旧版第一条"缺 sgCN/bnCN（~99%）"**已删除**——三个无此字段的 mod（JCY/MDK/ComG）在国服正常运行，该归因从未被实测支撑（见 §1 翻案）。
   - ⚠️ **纠错**：`data/hd/character/enemy/*hire.json` **实体 json（不含 .model）并未证实禁止**——JCY 国服在线版 ship 了 **131 个 enemy + 6 个 npc 实体 json、0 个 .model**，照常在线运行。会崩的是 **`.model` 文件** 和 **`data/global/excel/act*hire.json`（佣兵*数值/excel*）**。**别把"佣兵实体 json"与"佣兵 excel"混为一谈**（旧文档曾混淆并误标 hd 实体 json 为禁）。

### 模式 B：启动 ~20 秒无日志崩溃
- **根因：字符串条目缺 `id` 字段。** 引擎建字符串索引表时每条必须有数字 id，缺失直接崩、无日志。
- 修复：每条都补 id；自定义条目用 vanilla 最大 id 之上的高位段（见 §5）。

### 模式 C：进游戏后 DX12 DeviceLost 崩溃
- **根因：mod 的 JSON 引用了被国服"和谐替换"的底层美术资产**，国服替换后的 `.model` 顶点格式与国际版不同 → `Mesh vertex format is invalid` → DeviceLost。
- blz-log.txt 特征：
  ```
  [Render/4]: Mesh vertex format is invalid. Filename: 'data/hd/...'
  [Prism/4]: ...CopyCmdListImpl::End: Close Failed (0x80070057)
  [Prism/4]: ...Present Failed (DeviceLost 0x887a0005)
  ```
- 已知和谐冲突路径（删除 mod 内引用它们的 JSON，不是删 .model）：
  - `data/hd/vfx/meshes/lit_mesh/bonearmor/`（骨甲 VFX）
  - `data/hd/objects/shrines_other/`（鹿骷髅等祭坛，含 PhysicsCloth 顶点）
  - 其他含骨骼/骷髅/地狱/血腥意象的 `data/hd/objects/` 路径同理。

---

## 3. 文件安全速查表（国服在线，JCY 验证）

| 类型 | 路径 | 在线安全？ |
| --- | --- | --- |
| 字符串 JSON | `data/local/lng/strings/*.json` | ✅（sgCN/bnCN 非必需，见 §1 翻案；条目必须带 id） |
| Excel TXT（视觉类 states/overlay/sounds） | `data/global/excel/*.txt` | ✅ **在线可用** |
| Excel TXT（数值类 伤害/掉率/属性） | 同上 | ⚠️ 技术可用，但**改公平性=TOS 封号风险** |
| 环境模型 | `data/hd/env/model/**/*.model` | ✅ 安全 |
| **角色模型(二进制网格)** | `data/hd/character/**/*.model` | ❌ 结构性禁止（真正硬禁） |
| 角色/敌人/佣兵**实体 json**（不含 .model） | `data/hd/character/{enemy,npc}/*.json` | ✅ 安全（JCY ship 131+6 个，0 .model） |
| 佣兵**数值 excel** | `data/global/excel/act*hire.json` | ❌ 国服禁（启动~20s崩，同 .model 类） |
| 雇佣兵 UI 图标 | `data/hd/global/ui/hireables/` | ✅ 安全 |
| 和谐冲突资产 | `lit_mesh/bonearmor/`、`objects/shrines_other/` | ❌ DeviceLost |
| 贴图缓存 | `data/hd/texture_desc_cache.json` | ❌ 加载 4+ 分钟 |
| UI 布局（标准） | `data/global/ui/layouts/*.json` | ✅ |
| 贴图/Sprite/音效/Overlay/粒子 | `*.texture/*.sprite/*.flac/*.json` | ✅ |

> 🛑 **已纠正的错误结论**（社区 MDK 国服在线版验证）：
> - ❌"excel = 国服在线禁区" → ✅ `-mod` 模式 excel 在线可用，服务器不校验 mod 内 excel。
> - ❌"所有 .model 都要删" → ✅ 只有 `character/` 下的禁，`env/model/` 安全。
> - ❌"卡读取因为 excel" → ✅ 真因是版本号/texture_desc_cache/.model 类（见模式 A）。
> - ❌"缺 sgCN/bnCN 卡读取/国服不读 zhCN" → ✅ **已翻案**（2026-06-13）：国服原版数据无此二字段，客户端读 zhCN；JCY/MDK/ComG 均无此字段照常在线（见 §1）。
> - ❌"`character/enemy/*hire.json` 实体结构性禁止" → ⚠️ **真正硬禁是 `.model` 与 `excel/act*hire.json`**；佣兵/角色**实体 json 不含 .model 即无已知崩溃机制**（JCY 实证 ship 131 enemy+6 npc 实体 json）。旧文档把"佣兵 excel"与"佣兵实体 json"混淆而误标，已纠正。社区确有改佣兵外观的国服 mod。

---

## 4. 国服和谐（censorship）译名/资产对照

国服监管和谐针对：死亡/尸体/部位（防腐/僵尸/骷髅）、超自然（鬼/魂）、血腥（剥皮/剖尸）。

| 类别 | 英文 | 国际译名(zhTW/zhCN) | 国服和谐显示（运行时按 Key 替换） |
| --- | --- | --- | --- |
| 死灵副手 | Preserved/Zombie/…Head | …之首 | …头骨 |
| 鬼魂系装备 | Ghost X | 鬼魂X | 幽灵X |
| 宝石 | Skull | 骷髅 | 头骨宝石 / 头骨 |
| 怪物 | Soul Flayer / Collector | 剥皮灵魂/灵魂采集者 | 剥魂者/收魂者 |

> ⚠️ **资产层和谐**：骷髅宝石、死灵之首、鬼魂武器的 **2D sprite 在国服被替换**（骷髅→石英水晶图）。**图标**仍是和谐版，除非替换 sprite（高风险，一般不动）。怪物死亡尸体也被替换为石碑——**无 mod 参数可绕过**（`-assettestmode 1` 经实测**不存在**）。

> 🔓 **骷髅名和谐可绕过——靠 `namestr` 重定向（2026-06-03 实测生效；曾误判为"引擎硬锁"，此处已纠正）**
>
> **关键机制**：CN "石英"和谐**按物品 `namestr` 列引用的字符串 Key 拦截**，*不是*按 item-code。所以直接改 `item-names[skl]` 或 `bnet[skl]` 都**无效**——namestr 仍指向 `skl`，照样命中和谐表，回退显示"无瑕疵的石英"。（这解释了为何只改 zhCN 全名的老办法在新版客户端失效。）
>
> **绕过配方（三步）**：
> 1. 在 `item-names.json` **新建一个未被和谐的 Key**（id 用自定义高位段，如 30051+），值为你要的名字：
>    ```json
>    { "id": 30054, "Key": "suskl", "enUS": "ÿc5无骷ÿc0", "zhCN": "ÿc5无骷ÿc0" }
>    ```
>    （实测仅 `enUS`+`zhCN` 即在 CN 生效——这也是"国服读 zhCN"的直接证据之一，见 §1。）
> 2. 在 `data/global/excel/misc.txt` 把该物的 **`namestr` 列重定向到新 Key**（骷髅 5 行：`skc/skf/sku/skl/skz` → `suskc/suskf/susku/suskl/suskz`）。**`code` 列保持原值不动**（道具码、合成配方依赖它）。
> 3. **mod 内必须同梱 misc.txt**（excel 承重，缺了就回退和谐名）。改动极小（仅 namestr 单元格）、纯外观、无平衡数值改动。
>
> **可推广**：同法适用于其他 key 级和谐物（死灵之首、鬼魂武器等）——新建未被和谐的 Key + 把该物 excel 的 namestr 指过去。**注意 2D 图标仍是和谐版**（sprite 层另算，见上一条），此法只换显示名。
>
> **对照证据**：非骷髅宝石（无瑕紫 `gzv`→"无紫"）直接改 item-names 即生效，因为 `gzv` 不在和谐 Key 表里；骷髅 `sk*` 在表里，必须靠 namestr 旁路换一个表外 Key 才行。
>
> ⚠️ **封号视角**：此法要同梱 misc.txt（属 excel）。本改动是纯 namestr 重定向（外观，无平衡数值），风险等级与字符串 mod 相当；但若追求"零数据改动"极致安全（如红叶哲学），则它跨过了"不碰 excel"那条线——按需取舍。

---

## 5. 自定义条目 ID 规范

- vanilla id 有固定范围（不同版本不同，如某 CN 版 3333–28105）。
- **自定义新条目 id 必须高于 vanilla 最大值**（如从 30000+ 起），避免冲突。
- 缺 id = 模式 B 崩溃。新增条目模板：
```json
{ "id": 30051, "Key": "MyKey", "enUS": "...", "zhCN": "..." }
```
> 跨文件 id 重复（如 bnet/skills/ui 之间）是 vanilla 原版行为，**不是**问题。

### 5.1 ⚠️ id 是全局命名空间——给已有 vanilla 字符串编造新 id = 静默灾难

「跨文件同 id 没问题」仅指**同一个 Key 在多文件用它自己的 canonical id**。反例边界：

> **要把一个已存在的 vanilla 字符串补进另一个文件时（最常见：把宝石/骷髅名补进 `bnet.json` 去覆盖国服和谐名），必须复用该字符串自己的 canonical id（即它在 `item-names.json` 里的 id），绝不能临时编一个新 id，也不能用 30000+ 自定义段。**

**为什么**：id 是全局命名空间。你编的"新" id 很可能正好是**别的物品**的 id。后果有两层、且**无报错、不崩溃**：
1. 你的覆盖**静默失效**——引擎按目标字符串的真实 id 查找，你的条目挂在错 id 上，根本没接上 → 名字回退到 CASC 和谐值。
2. 你顺手**改坏了被撞 id 的那个物品**的名字。

**实测案例（2026-06-03）**：往 `bnet.json` 补骷髅名想盖掉"石英"，给 `skl` 编了 id `2654`。`skl` 真实 id 是 `2280`；而 `2654` 属于暗金物品 *The Face of Horror*。结果：无瑕骷髅仍显"无瑕疵的石英"（覆盖没接上），且恐怖之颜被悄悄改名。**改前必查目标 Key 在 `item-names.json` 的真实 id，原样复用。**

> 推论（覆盖国服和谐宝石/骷髅名的正确姿势）：参照已验证生效的 `gsg`(id 2254)/`gsw`(2263)——它们**仅在 bnet、用各自 canonical gem id**。补骷髅就用 `skc`2277/`skf`2278/`sku`2279/`skl`2280/`skz`2281。和谐 **2D 图标**仍改不掉（见 §4 末），只改名。

---

## 6. 国际服 → 国服 转换 SOP（可复用清单）

1. **版本号**：`dataversionbuild.txt` 改成当前游戏版本。
2. **删结构性禁止文件**：`character/**/*.model`（二进制网格，保留 `env/model/`）+ `data/global/excel/act*hire.json`（佣兵数值 excel）。**注意**：`character/{enemy,npc}/*.json` 实体 json（不含 .model）**不必删**，JCY 保留并在线运行。
3. **删和谐冲突资产引用**：`vfx/meshes/lit_mesh/bonearmor/`、`objects/shrines_other/`，以及 blz-log 报 `Mesh vertex format invalid` 的其他路径对应 JSON。
4. **删贴图缓存**：`texture_desc_cache.json`。
5. **删外语 mod 专属内容**：`Mod*.json` 自定义面板、外语 baked 面板（如 `Skillguide*Panelhd.json`）、超大外语 sprite（helpMaster 等）、非 D2R 职业图标。
6. **修所有字符串 JSON**：扫 `strings/` + `strings-legacy/`，确认每条带 `id` 与 `zhCN`，补色码前缀。（sgCN/bnCN 非必需；若源文件本来就带，改 zhCN 时同步改掉旧值即可。）
7. **minfo 最简**：`modinfo.json` 保持 `{"name":..., "savepath":...}`。

**翻译方向**：去国服和谐 → 用 zhTW 国际版繁体 → `zhconv` 转简体（`pip install zhconv`；`zhconv.convert(t,'zh-hans')`），**不用**国服 zhCN 和谐译名。

---

## 7. 排查顺序速记
- 卡读取 → 查版本号 → texture_desc_cache → `.model` 文件 / `excel/act*hire.json`（**非** character 实体 json）
- 20s 无日志崩 → 查字符串缺 id
- 进游戏 DeviceLost → blz-log 找 `Mesh vertex format invalid` → 删引用和谐资产的 JSON

# 06 · 国服(bnCN)兼容 · 和谐 · 防闪退完全指南

> D2R 国服(网易) mod 的核心难点都在这。本篇是 guide 最重要的实战章节，来自 JCY 源码 + blz-log 实测 + 社区(MDK/BUFF)联机验证。
> ⚠️ 含**已被纠正的错误结论**——别再踩。

---

## 1. 语言代码（locale）全表

| 字段 | 服务区域 | 客户端读取 |
| --- | --- | --- |
| `zhCN` | 国际服（暴雪/亚服 Battle.net 非大陆） | 简体中文 |
| `bnCN` | **国服（网易大陆）** | 简体中文（**国服读这个，不读 zhCN**） |
| `sgCN` | 松岗简体（legacy），国服 fallback | — |
| `zhTW` | 繁体（台港澳） | 繁体中文 |
| `sgTW` | 松崗繁體（legacy） | — |
| `enUS` | 英文 | — |

**铁律：每条字符串写完 `zhCN`，必须同步 `sgCN` + `bnCN`（有 zhTW 则同步 sgTW）。** 否则国服卡"正在读取"。JCY 实证做法：
```python
obj["sgCN"] = obj["zhCN"]
obj["bnCN"] = obj["zhCN"]
obj["sgTW"] = obj["zhTW"]   # 若有 zhTW
```

---

## 2. 国服三大故障模式（精确归因）

国服出问题就这三种，**对症排查、别瞎猜**：

### 模式 A：卡"正在读取"（加载失败/极慢）
按概率排查：
1. **字符串 JSON 缺 `sgCN`/`bnCN`**（最常见，~99%）。注意要扫 `strings/` **和** `strings-legacy/` 两个目录。
2. `dataversionbuild.txt` 版本号与当前游戏不一致。
3. 存在 `data/hd/texture_desc_cache.json`（不应在 mod 内 → 重验所有贴图，加载 4+ 分钟）。
4. 存在 `data/hd/character/**/*.model` 或 `data/hd/character/enemy/*hire.json`（结构性禁止）。

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
| 字符串 JSON（**含** sgCN/bnCN） | `data/local/lng/strings/*.json` | ✅ |
| 字符串 JSON（缺 sgCN/bnCN） | 同上 | ❌ 卡读取 |
| Excel TXT（视觉类 states/overlay/sounds） | `data/global/excel/*.txt` | ✅ **在线可用** |
| Excel TXT（数值类 伤害/掉率/属性） | 同上 | ⚠️ 技术可用，但**改公平性=TOS 封号风险** |
| 环境模型 | `data/hd/env/model/**/*.model` | ✅ 安全 |
| **角色模型** | `data/hd/character/**/*.model` | ❌ 结构性禁止 |
| 雇佣兵定义 | `data/hd/character/enemy/*hire.json` | ❌ 结构性禁止 |
| 雇佣兵 UI 图标 | `data/hd/global/ui/hireables/` | ✅ 安全 |
| 和谐冲突资产 | `lit_mesh/bonearmor/`、`objects/shrines_other/` | ❌ DeviceLost |
| 贴图缓存 | `data/hd/texture_desc_cache.json` | ❌ 加载 4+ 分钟 |
| UI 布局（标准） | `data/global/ui/layouts/*.json` | ✅ |
| 贴图/Sprite/音效/Overlay/粒子 | `*.texture/*.sprite/*.flac/*.json` | ✅ |

> 🛑 **已纠正的错误结论**（社区 MDK 国服在线版验证）：
> - ❌"excel = 国服在线禁区" → ✅ `-mod` 模式 excel 在线可用，服务器不校验 mod 内 excel。
> - ❌"所有 .model 都要删" → ✅ 只有 `character/` 下的禁，`env/model/` 安全。
> - ❌"卡读取因为 excel" → ✅ 真因几乎都是缺 sgCN/bnCN。

---

## 4. 国服和谐（censorship）译名/资产对照

国服监管和谐针对：死亡/尸体/部位（防腐/僵尸/骷髅）、超自然（鬼/魂）、血腥（剥皮/剖尸）。

| 类别 | 英文 | 国际(sgCN/zhTW) | 国服和谐(bnCN) |
| --- | --- | --- | --- |
| 死灵副手 | Preserved/Zombie/…Head | …之首 | …头骨 |
| 鬼魂系装备 | Ghost X | 鬼魂X | 幽灵X |
| 宝石 | Skull | 骷髅 | 头骨宝石 / 头骨 |
| 怪物 | Soul Flayer / Collector | 剥皮灵魂/灵魂采集者 | 剥魂者/收魂者 |

> ⚠️ **资产层和谐**：骷髅宝石、死灵之首、鬼魂武器的 **2D sprite 在国服被替换**（骷髅→石英水晶图）。改字符串能改回**名字**，但**图标仍是和谐版**，除非替换 sprite（高风险，一般不动）。怪物死亡尸体也被替换为石碑——**无 mod 参数可绕过**（`-assettestmode 1` 经实测**不存在**）。

---

## 5. 自定义条目 ID 规范

- vanilla id 有固定范围（不同版本不同，如某 CN 版 3333–28105）。
- **自定义新条目 id 必须高于 vanilla 最大值**（如从 30000+ 起），避免冲突。
- 缺 id = 模式 B 崩溃。新增条目模板：
```json
{ "id": 30051, "Key": "MyKey", "enUS": "...", "zhCN": "...", "sgCN": "...", "bnCN": "..." }
```
> 跨文件 id 重复（如 bnet/skills/ui 之间）是 vanilla 原版行为，**不是**问题。

---

## 6. 国际服 → 国服 转换 SOP（可复用清单）

1. **版本号**：`dataversionbuild.txt` 改成当前游戏版本。
2. **删结构性禁止文件**：`character/enemy/*hire.json`、`character/**/*.model`（保留 `env/model/`）。
3. **删和谐冲突资产引用**：`vfx/meshes/lit_mesh/bonearmor/`、`objects/shrines_other/`，以及 blz-log 报 `Mesh vertex format invalid` 的其他路径对应 JSON。
4. **删贴图缓存**：`texture_desc_cache.json`。
5. **删外语 mod 专属内容**：`Mod*.json` 自定义面板、外语 baked 面板（如 `Skillguide*Panelhd.json`）、超大外语 sprite（helpMaster 等）、非 D2R 职业图标。
6. **修所有字符串 JSON**：扫 `strings/` + `strings-legacy/`，补 `sgCN`/`bnCN`（有 zhTW 补 sgTW），补色码前缀。
7. **minfo 最简**：`modinfo.json` 保持 `{"name":..., "savepath":...}`。

**翻译方向**：去国服和谐 → 用 zhTW 国际版繁体 → `zhconv` 转简体（`pip install zhconv`；`zhconv.convert(t,'zh-hans')`），**不用**国服 zhCN 和谐译名。

---

## 7. 排查顺序速记
- 卡读取 → 查 sgCN/bnCN → 版本号 → texture_desc_cache → hire/model
- 20s 无日志崩 → 查字符串缺 id
- 进游戏 DeviceLost → blz-log 找 `Mesh vertex format invalid` → 删引用和谐资产的 JSON

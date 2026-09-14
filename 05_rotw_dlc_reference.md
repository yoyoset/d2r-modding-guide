# 05 · 2026《术士君临》DLC 事实参考

> D2R **《术士君临》(Reign of the Warlock)** 是真实官方扩展，**2026-02-11 发布**（含国服「术士君临」）。
> ⚠️ 提醒：知识库截止较早的 AI 可能误判其为"幻觉"——它是真的。涉及该版本内容前请联网核实最新细节。

---

## 1. 核心内容
- 新职业 **Warlock（术士）**：D2 25 年来首个新职业。可悬浮单手持双手武器、同时带副手。
- 三系技能树：**Demon（恶魔）/ Eldritch（异能）/ Chaos（混沌）**。
- 新副手物品类 **Grimoire（魔典/书）**：术士专属，可与双手武器同用。
- QoL：官方 **Loot Filter**、**Stash 堆叠页**（宝石/符文/材料堆叠至 99）。

---

## 2. 5 个新符文之语（已联网核实公式）

| 符文之语 | 公式（符文顺序） | 底材 |
| --- | --- | --- |
| **Authority**（威权/权威） | Hel + Shael + Ral | 身体防具 |
| **Coven**（女巫团） | Ist + Ral + Io | 头盔 |
| **Void**（虚空） | Thul + Zod + Ist | 匕首 |
| **Vigilance**（警惕） | Dol + Gul | 魔典/盾牌 |
| **Ritual**（仪式） | Amn + Shael + Ohm | 匕首 |

---

## 3. 术士暗金魔典（已核实存在）
- **Ars Al'Diabolos**（Blasphemous Grimoire，+2 混沌技能）
- **Ars Tor'Baalos**（+2 恶魔技能）
- **Ars Dul'Mephistos**（Occult Tome，+2 术士全技能）
- 另有 Measured Wrath、Hellwarden's Will 等新暗金。

---

## 4. 数据/兼容注意
- 魔典底材基础名（普通级）：Grimoire / Compendium / Tome / Codex / Old Book（分三档）。**具体物品代码需解包核实**，勿凭记忆。
- 堆叠靠 `misc.txt` 的 `AdvancedStashStackable` 列（=1 启用 99 堆叠）。
- 适配新版本时，覆盖 excel txt 风险高，优先注入式追加；务必用对应 patch 的 CASC 解包对齐。

---

## 5. 怎么判断"是不是 DLC 新增"（别把天梯季内容当 DLC）

> 证据级：📐 3.3.93847 excel 文件结构事实。实际踩过的坑：把天梯第 3 季的 解药/淬火/接地/火炉/壁垒/变形/嵌饰 当成 DLC 符文之语，把资料片老暗金「闇族碎滅者」当成 DLC 新暗金。

| 内容 | 判断依据 |
| --- | --- |
| 符文之语 | `runes.txt` 的 `firstLadderSeason` / `lastLadderSeason`。DLC 新增的 5 个（Authority / Coven / Void / Vigilance / Ritual）**两列都为空**；天梯季符文之语有季号。另外 `lastLadderSeason` 有值、早于当前季的，说明已经**不再限天梯**（如 Pattern/Plague/Mist 等 first=1、last=2）。标"(限天梯)"要同时看两列 |
| 暗金 | `uniqueitems.txt` 中 `Warlock Class Pack` 标记行**之后**的条目。3.3 新增：4 本魔典暗金、Dreadfang、Bloodpact Shard、Wraithstep、Gheed's Wager、Hellwarden's Will（Death Mask）、Sling / Opalvein（戒指）、Entropy Locket（护身符），以及 6 个 Colossal Jewel 暗金 |
| 巨型珠宝来源 | `monstats.txt` colossal1-3 地狱宝箱表 = `Uber Talic / Uber Madawc / Uber Korlic`（超级先祖）。`treasureclassex`：Talic → Defender's Bile/Fire，Madawc → Guardian's Light/Thunder，Korlic → Protector's Stone/Frost |

## 6. 破免板：普通 / 潜伏 / 新生（以 cubemain 为准，网上攻略有错）

> ⚠️ 已见过攻略网站写错（如"分筋裂骨 = 完美骷髅 + 蓝姆符文"）。**一律以 `cubemain.txt` + `uniqueitems.txt` 为准**。

- **普通破免板**：`spawnable` 为空，当前版本不再掉落；负面抗性在范围内随机（元素 -70~-90%、魔法 -45~-65%、物理 承伤 +10~20%）。
- **潜伏（PreCrafted）**：`spawnable=1`，物品等级 75，数值同普通版，用作合成材料。
- **新生（Crafted，代码 cs2）**：负面值**固定在范围最弱一端**（元素 -70%、魔法 -45%、承伤 +10%），另附加 5 条随机强化词缀（冰寒版 6 条）。

| 新生版 | 公式（方块，3.3 cubemain） |
| --- | --- |
| 毒 Rotting Fissure | 潜伏版 + Ko(#18) + 完美绿宝石 + 西方世界石碎片(xa1) |
| 冰 Cold Rupture | 潜伏版 + Lum(#17) + 完美蓝宝石 + 东方碎片(xa2) |
| 电 Crack of the Heavens | 潜伏版 + Fal(#19) + 完美黄玉 + 南方碎片(xa3) |
| 火 Flame Rift | 潜伏版 + Io(#16) + 完美红宝石 + 深层碎片(xa4) |
| 物理 Bone Break | 潜伏版 + Pul(#21) + 完美紫水晶 + 北方碎片(xa5) |
| 魔法 Black Cleft | 潜伏版 + Mal(#23) + 完美钻石 + 南方 + 深层 + 北方碎片 |

> 同一批公式在 cubemain 里还有"魔法物品 + 符文 + 完美宝石 + 碎片 → 穿透词缀装备"的版本，目前 `enabled=0`（未启用），别当成现行公式。

## 7. 官方名称

- 国服简中：**术士君临**（游戏 `ui.json` 原文 `RotWLong`）。
- 台港繁中：**術士軍臨**（战网港区商店页）。OpenCC 由简转繁得到的是"術士君臨"，做繁中版要单独映射。

> 本节为快速参考，**新增/变动细节以官方 + 社区(Maxroll/Icy Veins 等) 最新资料为准**。

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

> 本节为快速参考，**新增/变动细节以官方 + 社区(Maxroll/Icy Veins 等) 最新资料为准**。

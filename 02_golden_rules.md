# 02 · 铁律（动手改之前必读）

> 这些是"违反就翻车"的硬规则：改了不显示、启动闪退、双端不一致。每条都经实战验证。

---

## 1. CN 客户端读取优先级（改对文件）

D2R **国服(bnCN)客户端**对同一物品的不同部分，读取来源文件不同。**改错文件 = 改了也不显示。**

| 显示内容 | 权威来源 | 说明 |
| --- | --- | --- |
| 多数物品/宝石/符文名 | `item-names.json` | 常规名走这里 |
| 部分宝石名 | `bnet.json` | 有些宝石**只在** bnet.json，item-names 里没有 |
| **物品品质标签**（精良/Superior 等） | **`bnet.json`** | bnet 同名 key 会**抢显示**，覆盖 item-nameaffixes |
| 装备 tooltip **属性描述** | **`item-modifiers.json`** | 改此文件即生效（参考 mod「Colored Item Descriptions」） |

### 验证过的反直觉点
- **CN 确实会读 `item-names.json`**（标准紫宝石 gsv、无瑕黄 gly 都从这里正常显示）。"改 item-names 没用"这种一刀切说法**不成立**。
- 但**品质标签/部分宝石**被 `bnet.json` 抢——改 item-nameaffixes 无效时，去查 bnet.json 有没有同名 key。
- 个别物品（如某些 mod 里的骷髅）可能存在引擎级名称锁定，明明改了却显示原版/和谐名——**遇到改了不生效，先怀疑"改错文件"，并以游戏内实测为准**。

> 经验法则：拿不准时，**名字类两文件都写**（item-names + bnet），描述类只改 item-modifiers。最终以进游戏验证为准。

---

## 2. 三字段同步（CN 必须）

CN 客户端读 `sgCN`/`bnCN`，**不读** `zhCN`。每条改动必须三字段一致：

```python
entry["zhCN"] = "文本"
entry["sgCN"] = entry["zhCN"]   # CN 客户端读这个
entry["bnCN"] = entry["zhCN"]   # CN 客户端读这个（极重要）
```

> 名字类如需兼顾国际/繁中端，再同步 `zhTW`（按各文件既有约定：有的文件 zhTW 存全名、CN 三字段存简称）。

---

## 3. 防闪退红线（碰了 CN 必崩）

| 红线 | 后果 | 正确做法 |
| --- | --- | --- |
| 打包自定义 `.model`（3D 顶点文件） | CN 启动 ~20s 无日志闪退 | 编译末步递归删除 `data/hd/character` 下所有 `.model` |
| 覆盖佣兵 `act*hire.json` | CN 闪退 | 不打包佣兵配置文件 |
| 覆盖 `levels.txt` / `levels.bin`（结构） | 进特定地图瞬间崩 | 地图名只在 `levels.json` 改，**绝不**动结构 txt |
| 修改 `texture_desc_cache.json` | CN DX12 崩溃 | 不碰 |
| 字符串条目**缺 `id` 字段** | 启动 ~20s 无日志闪退 | 每条必须有 id；新增条目从权威源取真实 id，自定义用项目约定高位段 |
| 覆盖 `skills.txt`/`uniqueitems.txt`/`runes.txt` 结构 | 找不到 ID 崩 | 优先注入式追加，勿整文件物理覆盖；必要时先用最新 CASC 解包对齐 |

---

## 4. 字体/符号（防空白方块）

D2R 中文字体 Unicode 覆盖有限。loot 简称里用了字体**没有的符号**会显示为空白方块 `☐`。

- 用新符号前，**必须**用脚本载入 mod 实际 `.ttf` 验证该字符有字形轮廓（见 `tools/` 与 `04_styling_colors_symbols.md`）。
- 安全符号集见 `04`。需要更多符号时，用 fontTools 把目标 Unicode 区段从图标字体注入到中文字体。

---

## 5. 双端一致性

- 改动同时影响国服(bnCN/sgCN)与国际版(zhCN/zhTW)。优先按**国际版 zhTW 去和谐**译名，再简体化。
- UI 坐标改动**勿推出屏幕外**（如 `rect.x: -1394`）来"隐藏"面板——会导致功能锁死。用 `TogglePanel` 开关或还原坐标。
- 键鼠 HUD 的改动在**手柄模式不生效**（手柄读 `layouts/controller/`），需单独注入。

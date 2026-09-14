# 03 · 标准数据获取流程 + 物品代码参考

> 核心原则：**永不手敲、永不凭记忆猜代码/ID。一切从权威源提取，进游戏验证。**
> 触发教训：曾凭"规律"假设无瑕宝石代码是 `gzy/gzb…`，实际是 `gly/glb…`；按猜测造 id 会产生垃圾条目 → 游戏崩溃。

---

## 1. 为什么必须有流程

1. **缺 id 即崩溃**：每条字符串必须有 `id`，缺失 → 启动 ~20s 无日志闪退。id 绝不能发明。
2. **代码反直觉**：同类物品代码不连续、有历史怪癖（见 §4）。凭印象写代码 = 写错物品。
3. **读取源不唯一**：名字/描述/品质走不同文件（见 `02`）。改错文件 = 不显示。

---

## 2. 权威源优先级

| 优先级 | 源 | 用途 |
| ---: | --- | --- |
| 1 | 官方 CASC 解包数据（对应目标 patch 版本） | 最权威的 代码/id/原文 |
| 1 | 社区维护的"未和谐"基准字符串库（如 yup 系列） | 去和谐 zhTW + 英文 + id 的便捷来源 |
| 1 | 社区维护的完整 excel 镜像（如 [pinkufairy/D2R-Excel](https://github.com/pinkufairy/D2R-Excel)，按 patch 更新） | skills.txt / itemtypes.txt 等全量表，先 `git pull` 再用 |
| 2 | 目标客户端 CASC（如国服 bnCN） | 核对和谐名现状 |
| 3 | 成品 mod（参照做法） | **不作为译名/数据权威** |
| ✗ | AI 记忆 / 经验 / 训练数据 | **禁止作为代码或 id 来源** |

---

## 3. 标准提取流程（5 步）

```
1) 确定目标的【显示来源文件】   → 名字=item-names/bnet？描述=item-modifiers？(见 02)
2) grep 权威源确认真实 Key/代码 → 绝不假设拼写、大小写、怪癖
3) 用提取工具按 id 区间/Key 拉  → tools/extract_standard_data.py
4) 人工审阅生成的对照表         → 英文名↔代码↔id 一一对应，无和谐残留
5) 据此改文件 → 进游戏验证       → 截图交叉求证，通过才下一类
```

提取注意：
- D2R json 带 BOM → `open(path, encoding='utf-8-sig')`。
- 文本含色码字符 `\xff`('ÿ') → Windows 控制台输出前 `sys.stdout.reconfigure(encoding='utf-8')`，否则 GBK 报错。
  - ⚠️ 被别的脚本 `import` 的模块里**不要**写 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...)`：旧 wrapper 被回收时会关掉底层 buffer，主脚本随后 `ValueError: I/O operation on closed file`。统一用 `reconfigure`。

### 3.1 直接从本机 CASC 提取 / 枚举（CascLib）

社区镜像拿不到的文件（roomtiles、preset、overlay json、模型清单），或者要核对本机客户端版本时，用 CascLib（D2RMM 自带 `CascLib.dll`）直接读：

```python
import ctypes
lib = ctypes.CDLL(r"<D2RMM>\tools\CascLib.dll")
# 声明 argtypes/restype 后：
lib.CascOpenStorage(rb"<游戏目录>\Data:osi", 0, ctypes.byref(storage))   # 国服要带 :osi
lib.CascOpenFile(storage, rb"data:data\global\excel\states.txt", 0, 0, ctypes.byref(h))
# CascReadFile 循环读完；枚举用 CascFindFirstFile(storage, b"*act4_lava_river_flow*", ...)
```

- 路径格式：`data:data\` 前缀 + 反斜杠。在 bash heredoc 里写 Python 时反斜杠容易被吃掉，路径分隔符可以用 `chr(92)` 拼。
- `CascFindFirstFile` 用于"这个目录下到底有哪些文件"——例如用本机清单生成替换文件，而不是信任几年前的旧包。

### 3.2 镜像版本 ≠ 客户端版本，要核对

- 社区 excel 镜像通常跟国际服大版本，国服可能多一个热修号（例：镜像 3.3.93847、国服客户端 3.3.93854）。**用 CASC 提取本机 `global/excel/*.txt` 与镜像逐字节比对**，一致才可放心当权威（该例 91 个 txt 全一致）。
- 数据版本号两服可能不同：`dataversionbuild.txt` 国服 93854、国际服 93847（同一时期）。做双端 mod 要分开写。

### 3.3 第三方 mod 自带的 excel 可能是旧版本底

- 例：某 buff 图标 mod 的 `states.txt`/`overlay.txt` 基于 3.2 做——缺 3.3 新增的 `missilelimit`/`primeevil_threat` 两行，`bind_demon`/`chronicle*`/`apocalypse` 等是旧值。直接整文件覆盖会把游戏数据倒退。
- 做法：**以当前版本 excel 为底，只按列/按行合入 mod 真正改的部分**（该例 states 只取 `overlay1`/`removerlay` 两列，overlay 只追加新行并检查 id 不冲突）。先比对 mod 文件和它自带的 `base/` 原版，找出它到底改了什么列。

### 3.4 社区附件获取

- Inven（韩服）帖子附件是 `upload3.inven.co.kr/upload/<日期>/bbs/<文件>` 直链，带 `Referer` 可直接下载，无人机验证；部分大包放 Google Drive，需要手动下。
- 整合包作者停止分享时，整合包帖通常仍列出每个模块的**原作者和原帖**，按原帖逐个下载散件即可。

---

## 4. 物品代码 / ID 参考（已核实的公开 D2R 数据）

> 五级品质代码规律：碎裂`gc*` / 瑕疵`gf*` / 普通`gs*` / **无瑕`gl*`(唯无瑕紫例外=`gzv`)** / 完美`gp*`。
> 后缀：v紫 y黄 b蓝 g绿 r红 w钻。

### 宝石 (id 2236–2265)
| 品类 | 碎裂 | 瑕疵 | 普通 | 无瑕 | 完美 |
| --- | --- | --- | --- | --- | --- |
| 紫 Amethyst | gcv | gfv | gsv | **gzv** | gpv |
| 黄 Topaz | gcy | gfy | gsy | gly | gpy |
| 蓝 Sapphire | gcb | gfb | gsb | glb | gpb |
| 绿 Emerald | gcg | gfg | gsg | glg | gpg |
| 红 Ruby | gcr | gfr | gsr | glr | gpr |
| 钻 Diamond | gcw | gfw | gsw | glw | gpw |

### 骷髅 (id 2277–2281)
`skc`(碎) `skf`(瑕) `sku`(普通) `skl`(无瑕) `skz`(完美)

### 药水 (id 2266–2275)
生命 `hp1`–`hp5`（弱/轻/普通/强效/特效）；法力 `mp1`–`mp5`。

### 符文 (item-runes.json，key `r01`–`r33` / `r01L`–`r33L`)
`r01`=El … `r33`=Zod。注意是 `r16`/`r16L` 这种 key，**不是** `Rune16`。

---

## 5. ⚠️ 已知数据怪癖台账（凭直觉必错，持续补充）

| 怪癖 | 真相 | 危害 |
| --- | --- | --- |
| 无瑕宝石代码不统一 | 无瑕紫=`gzv`（唯一 gz），其余无瑕=`gl*`（gly/glb/glg/glr/glw） | 按 gzy 猜会造垃圾条目→崩 |
| 翡翠 id 顺序异常 | 无瑕 `glg`(2253) 排在 标准 `gsg`(2254) **之前** | 顺延猜 id 会张冠李戴 |
| 符文 key 格式 | 是 `r16`/`r16L`，不是 `Rune16` | 写错 key 改不到 |
| 部分宝石名只在 bnet | 标准蓝/绿/红/钻可能不在 item-names | 以为有，实际没有 |
| 品质标签 bnet 抢显示 | bnet 同名 key 覆盖 item-nameaffixes | 改 nameaffixes 无效 |
| 技能 ID 凭记忆必错 | `skill(NN)` 必查 skills.txt 的 `*Id` 列。实测记忆陷阱：圣骑区段有偏移（110=电抗光环/111=复仇/115=活力/118=圣电震击/121=天堂之拳）、26=扫射(非诱饵)、92=毒新星(93 才是骨魂) | 物品注解/wiki 张冠李戴 |
| 最大孔数不是 gemsockets 原值 | 实际上限 = min(weapons/armor.txt 的 `gemsockets`, itemtypes.txt 该 type 的 `MaxSockets3`) | 直接读 gemsockets 会标错上限 |

> 每发现一个新怪癖 → 回填本表。**任何代码都必须 grep 源文件确认，不可凭记忆。**

# -*- coding: utf-8 -*-
"""标准数据提取工具（通用 · 无本机路径）

用途：从权威源 item-names.json 按 id 区间提取 [代码/ID/英文/繁中]，
     生成可审阅、可存档的权威数据表。**永不手敲、不猜 id。**

原则（见 03_data_sop_and_codes.md）：
  - id 永远来自源文件，绝不发明（缺 id → 游戏启动 ~20s 无日志崩溃）
  - 代码(Key) 永远以源文件为准（已知陷阱：无瑕宝石多为 gl*，唯无瑕紫=gzv；翡翠 id 顺序异常）

用法：
  python extract_standard_data.py <item-names.json 路径> [-o 输出.md] [--ranges 2236-2281 ...]

示例：
  python extract_standard_data.py ./item-names.json -o ref_codes.md --ranges 2236-2265 2277-2281
"""
import json, re, sys, argparse

CODE = re.compile('\xffc.', re.S)   # ÿcX 色码

def clean(s):
    s = CODE.sub('', s or '').replace('\n', ' ')
    s = re.sub(r'\[[^\]]*\]', '', s)        # 去 [+3Amn=Sol] 升级提示
    s = re.sub(r'[ｻ-ｿﾻ-﾿]', '', s)          # 去半角噪声符
    return s.strip()

def load(p):
    with open(p, encoding='utf-8-sig') as f:   # D2R json 带 BOM
        return json.load(f)

def parse_range(r):
    lo, hi = r.split('-'); return int(lo), int(hi)

def main():
    sys.stdout.reconfigure(encoding='utf-8')   # 防 Windows GBK 因 'ÿ' 报错
    ap = argparse.ArgumentParser()
    ap.add_argument('source', help='item-names.json 路径（权威源）')
    ap.add_argument('-o', '--out', default='ref_item_codes_ids.md')
    ap.add_argument('--ranges', nargs='+', default=['2236-2265', '2266-2275', '2277-2281'],
                    help='id 区间，如 2236-2265')
    a = ap.parse_args()

    by_id = {e['id']: e for e in load(a.source) if isinstance(e, dict) and 'id' in e}

    lines = ['# 权威物品代码/ID 存档（自动提取，勿手改）\n',
             f'> 源：`{a.source}`。ID 与 Key 均直接来自源文件，未经任何人工猜测。\n']
    for r in a.ranges:
        lo, hi = parse_range(r)
        lines.append(f'\n## id {lo}–{hi}\n')
        lines.append('| id | Key | 英文名 | 繁中名 |')
        lines.append('| ---: | --- | --- | --- |')
        for i in range(lo, hi + 1):
            e = by_id.get(i)
            if e:
                lines.append(f"| {i} | `{e.get('Key','')}` | {clean(e.get('enUS',''))} | {clean(e.get('zhTW',''))} |")

    lines.append('\n> ⚠️ 怪癖：无瑕宝石多为 `gl*`(唯无瑕紫=`gzv`)；翡翠 `glg` id 在 `gsg` 之前。任何代码都需 grep 源确认。')
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {a.out}')

if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成手机归属地与douban loc_id的对应关系。

需要注意通讯区域划分和城市划分并不一致，有些城市会合并为一个通讯区域，
湖北江汉是将天门、潜江、仙桃三个城市合并为一个江汉地区的通讯区域。由于douban loc_id并没有
江汉地区这个地方，且武汉有个江汉区，所以本脚本会把江汉地区错误的对应到武汉市的loc_id，
这个错误没什么大的危害，先忽略。

另外，有些手机在网上查到的归属地仍然可能是上诉三个城市中的一个。
"""

from douban.loc import Loc, TYPE_CITY, TYPE_REGION, TYPE_DISTRICT, TYPE_PROVINCE, TYPE_WORLD
from shire.common.sqlstore import store

# 100000|World, 108088│中国(大陆)
TYPE_W_MAPPING = {
    TYPE_WORLD: -2,
    TYPE_REGION: -1,
    TYPE_PROVINCE: 0,
    TYPE_CITY: 1,
    TYPE_DISTRICT: 2,
}
ALL_LOCS = []


def _fill_all_locs():
    global ALL_LOCS
    all_loc_ids = [i for i, in store.execute('select id from loc;')]
    _ALL_LOCS = Loc.gets(all_loc_ids)
    for loc in _ALL_LOCS:
        if loc.type in (TYPE_REGION, TYPE_WORLD):
            continue
        parent = loc.parent()
        if not parent:
            continue
        grandpa = parent.parent()
        if not grandpa:
            continue
        if parent.type == TYPE_PROVINCE:
            ALL_LOCS.append((parent.name('cn'), loc))
        elif loc.parent_id == '108088':
            ALL_LOCS.append((loc.name('cn'), loc))
        elif parent.parent_id == '108088':
            ALL_LOCS.append((parent.name('cn'), loc))
        else:
            ALL_LOCS.append((grandpa.name('cn'), loc))


def _weight(w, loc):
    w += TYPE_W_MAPPING[loc.type]
    if loc.habitable:
        w += 5
    return w, loc


def _match(l):
    r = []
    level_w = 0
    for prov_name, loc in ALL_LOCS:
        if prov_name != l[0]:
            continue
        loc_name = loc.name('cn')
        if loc.type == TYPE_DISTRICT:
            loc = Loc.get(loc.parent_id)
        if l[1] == loc_name:
            r.append(_weight(level_w + 20, loc))
        elif l[1].startswith(loc_name):
            r.append(_weight(level_w + 10, loc))
        elif loc_name.startswith(l[1]):
            r.append(_weight(level_w + 5, loc))
    return r


def filter_by_weight(pairs):
    seen = set()
    top_w = pairs[0][0]
    for w, t in pairs:
        if (t,) in seen:
            continue
        seen.add((t,))
        if w == top_w:
            yield w, t


def match(l):
    r = _match(l)
    r = sorted(r, key=lambda x: x[0], reverse=True)
    if not r:
        return
    r = list(filter_by_weight(r))
    assert len(r) == 1
    return r[0][1]


def main():
    import csv
    _fill_all_locs()
    done = set()
    with open('./douban_phone_loc_mapping.csv', 'w') as file_:
        csvwt = csv.writer(file_, lineterminator='\n')
        with open('./phonedat.csv') as rfile_:
            csvrd = csv.reader(rfile_)
            for line in csvrd:
                key = (line[2], line[3])
                if key in done:
                    continue
                done.add(key)
                dou_loc = match(key)
                if dou_loc:
                    csvwt.writerow([dou_loc.id, line[2], line[3]])
                else:
                    print('/'.join(line))


if __name__ == '__main__':
    main()

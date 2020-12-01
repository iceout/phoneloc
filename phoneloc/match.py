#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from douban.loc import Loc


def is_loc_phone_match(loc_id, phone_loc):
    loc_id = str(loc_id)
    phone_loc = str(phone_loc)
    if not loc_id or loc_id in ('0', '100000', '108088'):
        return
    if not phone_loc or phone_loc == '100000':
        return
    if loc_id == phone_loc:
        return True
    # if phone_loc == '99999' and loc_id in ('128464', '128465', '128466', '108304'):
    #     return True
    if (loc_id in ('118254', '128464', '128465', '128466', '108304') and
            phone_loc in ('118254', '128464', '128465', '128466', '108304')):
        return True
    loc1 = Loc.get(loc_id)
    loc2 = Loc.get(phone_loc)
    if not loc1 or not loc2:
        return
    if loc1.parent_id == phone_loc or loc2.parent_id == loc_id:
        return True
    return False

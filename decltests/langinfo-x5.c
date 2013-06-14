/* baseline */
#include <langinfo.h>

char *f(nl_item a)
{
  return nl_langinfo(a);
}

void nlitems(void)
{
  nl_item
    aa = CODESET,
    ab = D_T_FMT,
    ac = D_FMT,
    ad = T_FMT,
    ae = T_FMT_AMPM,
    af = AM_STR,
    ag = PM_STR,
    ah = DAY_1,
    ai = DAY_2,
    aj = DAY_3,
    ak = DAY_4,
    al = DAY_5,
    am = DAY_6,
    an = DAY_7,
    ao = ABDAY_1,
    ap = ABDAY_2,
    aq = ABDAY_3,
    ar = ABDAY_4,
    as = ABDAY_5,
    at = ABDAY_6,
    au = ABDAY_7,
    av = MON_1,
    aw = MON_2,
    ax = MON_3,
    ay = MON_4,
    az = MON_5,
    ba = MON_6,
    bb = MON_7,
    bc = MON_8,
    bd = MON_9,
    be = MON_10,
    bf = MON_11,
    bg = MON_12,
    bh = ABMON_1,
    bi = ABMON_2,
    bj = ABMON_3,
    bk = ABMON_4,
    bl = ABMON_5,
    bm = ABMON_6,
    bn = ABMON_7,
    bo = ABMON_8,
    bp = ABMON_9,
    bq = ABMON_10,
    br = ABMON_11,
    bs = ABMON_12,
    bt = ERA,
    bu = ERA_D_FMT,
    bv = ERA_D_T_FMT,
    bw = ERA_T_FMT,
    bx = ALT_DIGITS,
    by = RADIXCHAR,
    bz = THOUSEP,
    ca = YESEXPR,
    cb = NOEXPR,
    cc = YESSTR,
    cd = NOSTR,
    ce = CRNCYSTR;
}

"""Sdílené pomocné funkce pro rebrand prezentace (python-pptx + lxml)."""
import os
import re

from pptx import Presentation
from pptx.oxml.ns import qn

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, '..', '..', 'Power World R290 Helios Series Introduction.pptx')
REBUILT = {2, 4}          # snímky postavené znovu (build.py), z překladu vynechány


def rename_models(t):
    """Typová označení výrobce → REO HEATING (1F/3F = počet fází)."""
    def full(m):
        nums, ph = m.group(1).split('/'), m.group(2)
        big = {'20': 'RHX30', '30': 'RHX40'}
        if all(n in big for n in nums):
            return '/'.join(big[n] for n in nums)
        return 'RH' + '/'.join(nums) + f' {ph}F'
    t = re.sub(r'PW(\d{2}(?:/\d{2})*)-DKXLRE(\d)-H8', full, t)
    t = re.sub(r'PW(\d{2}(?:/\d{2})*)\s*KW', lambda m: 'RH' + m.group(1), t)
    t = re.sub(r'\bPW(\d{2})\b', lambda m: {'20': 'RHX30', '30': 'RHX40'}.get(m.group(1), 'RH' + m.group(1)), t)
    t = re.sub(r'Power\s*World', 'REO HEATING', t, flags=re.I)
    t = re.sub(r'Helios\s*Pro', 'REO R290 Smart', t, flags=re.I)
    return t


def fmt_key(r):
    """Formát runu bez nepodstatných atributů (lang, dirty, err…) — pro slučování runů."""
    rpr = r.find(qn('a:rPr'))
    if rpr is None:
        return ''
    a = {k: v for k, v in rpr.attrib.items() if k not in ('lang', 'altLang', 'dirty', 'err', 'noProof', 'kern', 'spc')}
    kids = []
    for c in rpr:
        tag = c.tag.split('}')[1]
        if tag in ('latin', 'ea', 'cs', 'sym'):
            continue
        kids.append(tag + str(sorted(c.attrib.items())) + ''.join(
            x.tag.split('}')[1] + str(sorted(x.attrib.items())) for x in c.iter() if x is not c))
    return str(sorted(a.items())) + '|'.join(kids)


def iter_paragraphs(slide):
    """(id, a:p element, kontejner) pro všechny odstavce na snímku — tvary, skupiny, tabulky."""
    sp_tree = slide.shapes._spTree
    n = 0
    for txbody in sp_tree.iter(qn('p:txBody'), qn('a:txBody')):
        for p in txbody.findall(qn('a:p')):
            yield n, p, txbody
            n += 1


def runs(p):
    return [r for r in p if r.tag in (qn('a:r'), qn('a:fld'))]


def para_text(p):
    return ''.join((r.find(qn('a:t')).text or '') for r in runs(p) if r.find(qn('a:t')) is not None)


def groups(p):
    """Sloučí po sobě jdoucí runy se stejným formátem → seznam (formát, [runy]); zalomení = ('br', [a:br])."""
    out = []
    for r in p:
        if r.tag == qn('a:br'):
            out.append(('br', [r]))
            continue
        if r.tag not in (qn('a:r'), qn('a:fld')):
            continue
        if r.tag == qn('a:fld'):
            out.append(('fld' + str(id(r)), [r]))
            continue
        k = fmt_key(r)
        if out and out[-1][0] == k:
            out[-1][1].append(r)
        else:
            out.append((k, [r]))
    return out


def text_groups(p):
    """Skupiny runů bez zalomení: [(formát, [runy])]."""
    return [g for g in groups(p) if g[0] != 'br']


def to_tagged(p):
    """Text odstavce; zalomení = <br>; při více formátech vyznačení <f1>…</f1>, <f2>…</f2>."""
    g = groups(p)
    tg = text_groups(p)
    multi = len(tg) > 1
    out, i = [], 0
    for k, rs in g:
        if k == 'br':
            out.append('<br>')
            continue
        i += 1
        t = ''.join((r.find(qn('a:t')).text or '') for r in rs)
        out.append(f'<f{i}>{t}</f{i}>' if multi else t)
    return ''.join(out)

"""Minimal MD -> HTML -> DOCX (macOS textutil) for the SOD draft. Usage: python3 src/md2docx.py"""
import re, html, subprocess, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
md = (root/'SOD-kotelna-BD-Michal.md').read_text()

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'\1', t)
    return t

out, lines, i = [], md.split('\n'), 0
stack = []  # open list tags
base = 0
def close_lists():
    while stack: out.append('</%s>' % stack.pop())
para = []
def flush():
    if para: out.append('<p>%s</p>' % inline(' '.join(para))); para.clear()
while i < len(lines):
    l = lines[i]
    if l.startswith('|') and i+1 < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i+1]):
        flush(); close_lists()
        rows = [l]; i += 2
        while i < len(lines) and lines[i].startswith('|'): rows.append(lines[i]); i += 1
        out.append('<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;width:100%">')
        for k, r in enumerate(rows):
            cells = [c.strip() for c in r.strip().strip('|').split('|')]
            tag = 'th' if k == 0 else 'td'
            out.append('<tr>' + ''.join('<%s style="font-size:9pt;text-align:left;vertical-align:top">%s</%s>' % (tag, inline(c), tag) for c in cells) + '</tr>')
        out.append('</table>'); continue
    m = re.match(r'^(#{1,4}) (.*)', l)
    if m:
        flush(); close_lists(); n = len(m.group(1))
        out.append('<h%d>%s</h%d>' % (n, inline(m.group(2)), n)); i += 1; continue
    if l.strip() == '---':
        flush(); close_lists(); out.append('<hr/>'); i += 1; continue
    if l.startswith('> '):
        flush(); close_lists(); out.append('<p style="margin-left:18pt;color:#555"><i>%s</i></p>' % inline(l[2:])); i += 1; continue
    m = re.match(r'^(\s*)(- |\d+\. )(.*)', l)
    if m:
        flush()
        if not stack: base = len(m.group(1))
        depth = max(1, (len(m.group(1)) - base) // 2 + 1)
        kind = 'ul' if m.group(2) == '- ' else 'ol'
        while len(stack) > depth: out.append('</%s>' % stack.pop())
        if len(stack) < depth: out.append('<%s>' % kind); stack.append(kind)
        text = m.group(3); i += 1
        while i < len(lines) and re.match(r'^\s{2,}\S', lines[i]) and not re.match(r'^\s*(- |\d+\. )', lines[i]):
            text += ' ' + lines[i].strip(); i += 1
        out.append('<li>%s</li>' % inline(text)); continue
    if not l.strip():
        flush(); close_lists(); i += 1; continue
    if re.match(r'^[a-z]\) |^\d+\.\d+ ', l): flush()
    close_lists(); para.append(l.strip()); i += 1
flush(); close_lists()
doc = ('<html><head><meta charset="utf-8"><title>SOD kotelna BD Michal</title><style>'
       'body{font-family:Calibri,Arial;font-size:11pt}h1{font-size:18pt}h2{font-size:15pt;margin-top:18pt}'
       'h3{font-size:12pt;margin-top:12pt}h4{font-size:11pt}</style></head><body>' + '\n'.join(out) + '</body></html>')
h = root/'src'/'SOD-kotelna-BD-Michal.html'; h.write_text(doc)
subprocess.run(['textutil', '-convert', 'docx', '-output', str(root/'SOD-kotelna-BD-Michal.docx'), str(h)], check=True)
print('ok')

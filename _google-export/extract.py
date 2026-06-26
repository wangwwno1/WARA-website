import re
import html as html_mod

with open('WARA.html', 'r', encoding='utf-8') as f:
    raw = f.read()

# Fix JS unicode escapes globally FIRST
raw = raw.replace('\\u003d', '=')
raw = raw.replace('\\u0026', '&')

# Extract YouTube URLs BEFORE removing scripts
# (they're embedded in JSON inside script tags)
yt = re.findall(
    r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
    raw
)
yt = sorted(set(yt))

# Also extract embed titles
titles = {}
for vid in yt:
    m = re.search(rf'youtube\.com/watch\?v={vid}","embed-title","([^"]+)"', raw)
    if m:
        titles[vid] = m.group(1)

# Now remove scripts, styles, noscript for text extraction
clean = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL)
clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
clean = re.sub(r'<noscript[^>]*>.*?</noscript>', '', clean, flags=re.DOTALL)

# Decode HTML entities
clean = html_mod.unescape(clean)

# Extract readable text blocks
texts = re.findall(r'>([^<>]{25,})<', clean)
seen = set()
result = []
for t in texts:
    s = t.strip()
    if s and s not in seen and not s.startswith('{') and 'function' not in s[:30]:
        seen.add(s)
        result.append(s)

with open('extracted_content.txt', 'w', encoding='utf-8') as f:
    f.write(f'=== YOUTUBE LINKS ({len(yt)} total) ===\n\n')
    for vid in yt:
        title = titles.get(vid, '?')
        f.write(f'https://youtu.be/{vid}\n')
        f.write(f'  Title: {title}\n\n')

    f.write(f'=== PAGE TEXT CONTENT ({len(result)} blocks) ===\n\n')
    for t in result:
        f.write(t.strip()[:500] + '\n---\n')

print(f'Done: {len(yt)} YouTube links, {len(result)} text blocks')

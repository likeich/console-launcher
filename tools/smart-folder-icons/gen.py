import os, subprocess, sys, random
OUT = sys.argv[1]  # themes/icons root
SRC = sys.argv[2]  # svg source root
IDS = {
 'smart-multiplayer':('MULTIPLAYER','#4f7dff','#1f3fb8'),
 'smart-coop':('CO-OP','#3fc28a','#11784d'),
 'smart-versus':('VERSUS','#ff5a4e','#a8121c'),
 'smart-rpg':('RPG','#9b6bff','#4b23a8'),
 'smart-platformer':('PLATFORMER','#ffb238','#c2560c'),
 'smart-racing':('RACING','#5a6378','#1e2330'),
 'smart-fighting':('FIGHTING','#ff7a3d','#b02a12'),
 'smart-shooter':('SHOOTER','#7d8a4e','#343d1c'),
 'smart-puzzle':('PUZZLE','#2fc4d6','#0d6f8f'),
 'smart-sports':('SPORTS','#ff9a2e','#b84a08'),
 'smart-never-played':('UNPLAYED','#ff6fb5','#a3166a'),
 'smart-recently-played':('RECENT','#4fb3ff','#14589e'),
 'smart-favorites':('FAVORITES','#ff4f79','#a3102f'),
 'smart-most-played':('MOST PLAYED','#ffcc3d','#b8780a'),
}
def person(x,y,s): return f'<circle cx="{x}" cy="{y-11*s}" r="{8*s}"/><path d="M{x-14*s} {y+18*s} v-6 a{14*s} {14*s} 0 0 1 {28*s} 0 v6 z"/>'
def star4(x,y,r): return f'<path d="M{x} {y-r} Q{x} {y} {x+r} {y} Q{x} {y} {x} {y+r} Q{x} {y} {x-r} {y} Q{x} {y} {x} {y-r}Z"/>'
def sword(rot): return (f'<g transform="rotate({rot} 50 50)"><path d="M50 6 L56 15 V60 H44 V15 Z"/><rect x="34" y="60" width="32" height="7" rx="3"/>'
  f'<rect x="46.5" y="67" width="7" height="17"/><circle cx="50" cy="88" r="5.5"/></g>')
def glyph(i, u):
  """White-on-transparent glyph in a 100x100 box. u: unique suffix for mask ids. Uses fill/stroke=inherit via currentColor."""
  S='stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"'
  return {
  'smart-multiplayer': f'<g opacity=".75">{person(24,54,.95)}{person(76,54,.95)}</g>{person(50,50,1.2)}',
  'smart-coop': f'{person(32,56,1.1)}{person(68,56,1.1)}<path d="M50 34 C40 27 37 22 37 18 C37 13 41 10 44.5 10 C47 10 49 12 50 14 C51 12 53 10 55.5 10 C59 10 63 13 63 18 C63 22 60 27 50 34Z"/>',
  'smart-versus': '<path d="M58 4 L30 54 H48 L40 96 L72 40 H53 Z" opacity=".45"/><text x="50" y="66" text-anchor="middle" font-family="Noto Sans" font-weight="900" font-style="italic" font-size="46">VS</text>',
  'smart-rpg': sword(45)+sword(-45),
  'smart-platformer': f'<rect x="8" y="70" width="26" height="24" rx="3"/><rect x="38" y="56" width="26" height="38" rx="3"/><rect x="68" y="42" width="26" height="52" rx="3"/><path d="M18 62 Q30 18 70 22" {S} stroke-width="4" stroke-dasharray="1 9"/>{person(80,24,.75)}',
  'smart-racing': '<rect x="14" y="8" width="6" height="86" rx="3"/>' + ''.join(f'<rect x="{22+c*12}" y="{12+r*12}" width="12" height="12"/>' for r in range(4) for c in range(6) if (r+c)%2==0) + f'<rect x="22" y="12" width="72" height="48" {S} stroke-width="3"/>',
  'smart-fighting': ''.join(f'<rect x="{28+k*12.5}" y="22" width="11" height="26" rx="5.5"/>' for k in range(4)) + '<rect x="27" y="38" width="50" height="40" rx="11"/><rect x="18" y="44" width="30" height="13" rx="6.5" transform="rotate(-12 33 50)"/><rect x="38" y="76" width="30" height="14" rx="3"/>' + f'<path d="M6 30 H18 M4 46 H16 M6 62 H18" {S} stroke-width="4"/>',
  'smart-shooter': f'<circle cx="50" cy="50" r="27" {S} stroke-width="7"/><path d="M50 6 V30 M50 70 V94 M6 50 H30 M70 50 H94" {S} stroke-width="7"/><circle cx="50" cy="50" r="6"/>',
  'smart-puzzle': f'<mask id="m{u}"><rect width="100" height="100" fill="#fff"/><circle cx="50" cy="82" r="10" fill="#000"/><circle cx="18" cy="50" r="10" fill="#000"/></mask><g mask="url(#m{u})"><rect x="16" y="22" width="60" height="60" rx="5"/><circle cx="46" cy="20" r="11"/><circle cx="78" cy="52" r="11"/></g>',
  'smart-sports': f'<mask id="m{u}"><rect width="100" height="100" fill="#fff"/><g stroke="#000" stroke-width="4" fill="none"><path d="M50 10 V90 M10 50 H90"/><path d="M24 20 Q42 50 24 80"/><path d="M76 20 Q58 50 76 80"/></g></mask><circle cx="50" cy="50" r="40" mask="url(#m{u})"/>',
  'smart-never-played': star4(42,56,36)+star4(78,22,15)+star4(80,78,10),
  'smart-recently-played': f'<path d="M20 50 A30 30 0 1 0 29 28.8" {S} stroke-width="8"/><path d="M14 22 L36 18 L32 40 Z"/><path d="M50 32 V52 L64 60" {S} stroke-width="7"/>',
  'smart-favorites': '<path d="M50 88 C18 66 8 50 8 34 C8 20 19 11 31 11 C40 11 47 17 50 24 C53 17 60 11 69 11 C81 11 92 20 92 34 C92 50 82 66 50 88Z"/>',
  'smart-most-played': f'<path d="M27 10 H73 V34 C73 52 63 62 50 62 C37 62 27 52 27 34 Z"/><path d="M27 18 H15 C15 34 21 42 31 44 M73 18 H85 C85 34 79 42 69 44" {S} stroke-width="6"/><rect x="45" y="60" width="10" height="14"/><rect x="31" y="74" width="38" height="12" rx="3"/>',
  }[i]
def esc(s): return s.replace('&','&amp;')
def minimal(i,lab,a,b):
  fs = 64 if len(lab)<=7 else (52 if len(lab)<=9 else 44)
  return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient></defs>
<rect width="512" height="512" fill="url(#g)"/>
<g transform="translate(146 70) scale(2.2)" fill="#fff" color="#fff">{glyph(i,'a')}</g>
<text x="256" y="420" text-anchor="middle" fill="#fff" font-family="Noto Sans" font-weight="900" font-size="{fs}" letter-spacing="1">{esc(lab)}</text></svg>'''
def colorful(i,lab,a,b):
  ext=''.join(f'<g transform="translate(0 {k*0.45})" fill="{b}" color="{b}" filter="brightness(.7)">{glyph(i,"e%d"%k)}</g>' for k in range(8,0,-1))
  return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
<defs><linearGradient id="g" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
<filter id="dark"><feColorMatrix type="matrix" values=".6 0 0 0 0  0 .6 0 0 0  0 0 .6 0 0  0 0 0 1 0"/></filter></defs>
<ellipse cx="540" cy="930" rx="330" ry="38" fill="#000" opacity=".38" filter="url(#blur)"/>
<g transform="translate(180 150) scale(7.2)">
<g filter="url(#dark)">{''.join(f'<g transform="translate(0 {k*0.45})" fill="{b}" color="{b}">{glyph(i,"e%d"%k)}</g>' for k in range(8,0,-1))}</g>
<g fill="{a}" color="{a}">{glyph(i,'f')}</g>
<g fill="url(#g)" color="#fff" opacity=".9">{glyph(i,'h')}</g>
</g></svg>'''
def xretro(i,lab,a,b):
  rnd=random.Random(i); x=250; bars=''
  while x<352:
    w=rnd.choice([1,1,2,3]); bars+=f'<rect x="{x}" y="318" width="{w}" height="30"/>'; x+=w+rnd.choice([1,2,2,3])
  stripes=''.join(f'<path d="M{64+k*24} 30 l-60 270" stroke="#fff" stroke-opacity=".07" stroke-width="10"/>' for k in range(16))
  fs = 30 if len(lab)<=8 else 24
  return f'''<svg xmlns="http://www.w3.org/2000/svg" width="369" height="369" viewBox="0 0 369 369">
<defs><linearGradient id="case" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f4f7"/><stop offset="1" stop-color="#c6c6ce"/></linearGradient>
<linearGradient id="art" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".42" r=".55"><stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<clipPath id="ap"><rect x="64" y="30" width="299" height="270"/></clipPath>
<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000" flood-opacity=".45"/></filter></defs>
<rect width="369" height="369" fill="url(#case)"/>
<rect x="0" y="0" width="58" height="369" fill="{b}"/><rect x="0" y="0" width="58" height="369" fill="url(#art)" opacity=".6"/>
<rect x="8" y="10" width="42" height="42" rx="6" fill="#fff"/><text x="29" y="40" text-anchor="middle" fill="{b}" font-family="Noto Sans" font-weight="900" font-size="22">CL</text>
<text transform="translate(40 352) rotate(-90)" fill="#fff" font-family="Noto Sans" font-weight="900" font-size="{fs}" letter-spacing="1">{esc(lab)}</text>
<rect x="64" y="8" width="299" height="18" fill="#2a2a30"/><text x="213.5" y="22" text-anchor="middle" fill="#fff" font-family="Noto Sans" font-weight="700" font-size="11" letter-spacing="3">CONSOLE LAUNCHER COLLECTION</text>
<g clip-path="url(#ap)"><rect x="64" y="30" width="299" height="270" fill="url(#art)"/>{stripes}<rect x="64" y="30" width="299" height="270" fill="url(#glow)"/></g>
<g transform="translate(128 52) scale(1.7)" fill="#fff" color="#fff" filter="url(#sh)">{glyph(i,'x')}</g>
<rect x="64" y="30" width="299" height="270" fill="none" stroke="#000" stroke-opacity=".25"/>
<text x="70" y="326" fill="#2a2a30" font-family="Noto Sans" font-weight="900" font-size="15">{esc(lab)}</text>
<text x="70" y="344" fill="#55555e" font-family="Noto Sans" font-weight="600" font-size="10">SMART FOLDER</text>
<rect x="246" y="312" width="110" height="42" fill="#fff"/><g fill="#111">{bars}</g></svg>'''
PACKS={'minimal-cl':(minimal,'png'),'colorful':(colorful,'webp'),'x-retro':(xretro,'png')}
for p in sys.argv[3:]:
  f,ext=PACKS[p]; os.makedirs(f'{SRC}/{p}',exist_ok=True)
  for i,(lab,a,b) in IDS.items():
    svg=f'{SRC}/{p}/{i}.svg'; open(svg,'w').write(f(i,lab,a,b))
    png=f'/tmp/cl-icons-work/{p}-{i}.png'
    subprocess.run(['rsvg-convert','-o',png,svg],check=True)
    dst=f'{OUT}/{p}/icons/{i}.{ext}'
    if p=='minimal-cl': subprocess.run(['convert',png,'-alpha','off','-strip',dst],check=True)
    elif ext=='webp': subprocess.run(['convert',png,'-quality','90','-define','webp:alpha-quality=100',dst],check=True)
    else: subprocess.run(['convert',png,'-strip',dst],check=True)

#!/usr/bin/env python3
"""Build index.html from resume.md"""
import re, html

def parse_md(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    data = {'name': '', 'name_cn': '', 'title_en': '', 'title_zh': '',
            'contacts': [], 'summary_en': '', 'summary_zh': '',
            'skills': [], 'projects': [], 'early': [], 'education': ''}

    # Name
    m = re.search(r'^# (.+)', content, re.M)
    if m:
        parts = m.group(1).split()
        data['name'] = parts[0] + ' ' + parts[1] if len(parts) > 1 else parts[0]
        data['name_cn'] = parts[-1] if len(parts) > 2 else ''

    # Title
    m = re.search(r'^\*\*(.+?)\*\*', content, re.M)
    if m:
        parts = m.group(1).split('|')
        data['title_en'] = parts[0].strip()
        data['title_zh'] = parts[1].strip() if len(parts) > 1 else ''

    # Contacts
    for c in re.findall(r'^- (.+)', content[:500], re.M):
        data['contacts'].append(c.strip())

    # Summary
    sm = re.search(r'## Summary.*?\n\n(.+?)\n\n---', content, re.S)
    if sm:
        text = sm.group(1).strip()
        lines = text.split('\n')
        data['summary_en'] = lines[0].strip()
        data['summary_zh'] = lines[1].strip() if len(lines) > 1 else ''

    # Skills
    skills_m = re.search(r'## Core Skills.*?\n(.*?)---', content, re.S)
    if skills_m:
        for line in skills_m.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('- **'):
                m2 = re.match(r'- \*\*(.+?)\*\* — (.+)', line)
                if m2:
                    data['skills'].append({'name': m2.group(1), 'desc': m2.group(2)})

    # Projects
    def parse_projects(section_text):
        items = []
        blocks = re.split(r'\n### ', section_text)
        for block in blocks[1:]:
            lines = block.strip().split('\n')
            title = lines[0].strip()
            meta_m = re.match(r'\*\*(.+?) · (.+?)\*\*', lines[1]) if len(lines) > 1 else None
            company = meta_m.group(1) if meta_m else ''
            period = meta_m.group(2) if meta_m else ''
            tags = re.findall(r'`([^`]+)`', lines[2]) if len(lines) > 2 else []
            rest = '\n'.join(lines[3:]).strip()
            paras = [p.strip() for p in rest.split('\n\n') if p.strip() and not p.strip().startswith('---')]
            desc_en = paras[0] if paras else ''
            desc_zh = paras[1] if len(paras) > 1 else ''
            items.append({'title': title, 'company': company, 'period': period,
                          'tags': tags, 'desc_en': desc_en, 'desc_zh': desc_zh})
        return items

    proj_m = re.search(r'## Project Experience.*?\n(.*?)## Early Career', content, re.S)
    if proj_m:
        data['projects'] = parse_projects(proj_m.group(1))

    early_m = re.search(r'## Early Career.*?\n(.*?)## Education', content, re.S)
    if early_m:
        data['early'] = parse_projects(early_m.group(1))

    # Education
    edu_m = re.search(r'## Education.*?\n\n\*\*(.+?)\*\*\n(.+)', content, re.S)
    if edu_m:
        data['education'] = {'school': edu_m.group(1).strip(),
                             'detail': edu_m.group(2).strip().split('\n')[0]}

    return data


def tag_class(tag):
    frameworks = {'AI Agent','NLP','MQTT','GraphQL','Kubernetes','DevOps','VueX',
                  'PKI','RSA','SM2/SM3/SM4','AES/DES','Mobile Architect','Team Lead'}
    langs = {'Dart','Swift','Objective-C','Java','TypeScript','JavaScript','C/C++','Vue'}
    if tag in frameworks: return 'tag-framework'
    if tag in langs: return 'tag-lang'
    return 'tag-platform'


def render_tags(tags):
    return ''.join(f'<span class="tag {tag_class(t)}">{html.escape(t)}</span>' for t in tags)


def render_timeline(items, section_num):
    out = []
    for item in items:
        out.append(f'''
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-card">
          <div class="timeline-meta">
            <span class="timeline-company">{html.escape(item["company"])}</span>
            <span class="timeline-period" data-en="{html.escape(item["period"])}" data-zh="{html.escape(item["period"].replace("Present","至今"))}">{html.escape(item["period"])}</span>
          </div>
          <h3>{html.escape(item["title"])}</h3>
          <p data-en="{html.escape(item["desc_en"])}" data-zh="{html.escape(item["desc_zh"])}">{html.escape(item["desc_en"])}</p>
          <div class="tech-tags">{render_tags(item["tags"])}</div>
        </div>
      </div>''')
    return '\n'.join(out)


def build(md_path='resume.md', out_path='index.html'):
    d = parse_md(md_path)

    contacts_html = ''.join(f'<div class="contact-item">{html.escape(c)}</div>' for c in d['contacts'])

    skills_html = ''
    icons = ['📱','🌐','🔐','🤖','🏗️','🌍']
    for i, s in enumerate(d['skills']):
        icon = icons[i] if i < len(icons) else '⚡'
        skills_html += f'''
      <div class="skill-card">
        <div class="skill-icon">{icon}</div>
        <h3>{html.escape(s["name"])}</h3>
        <p>{html.escape(s["desc"])}</p>
      </div>'''

    projects_html = render_timeline(d['projects'], 2)
    early_html = render_timeline(d['early'], 3)

    edu = d['education']
    edu_parts = edu['detail'].split('·') if isinstance(edu, dict) else []
    edu_en = edu['detail'] if isinstance(edu, dict) else ''
    edu_zh_parts = [p.strip() for p in edu_parts]

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE.format(
            contacts=contacts_html,
            skills=skills_html,
            projects=projects_html,
            early=early_html,
            edu_school=html.escape(edu['school']) if isinstance(edu, dict) else '',
            edu_detail=html.escape(edu_en),
        ))
    print(f'Built {out_path}')


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Andrew Wang 汪奇伟 — Resume</title>
<style>
  :root {{
    --primary: #0066cc;
    --secondary: #6b21e8;
    --accent: #e53e3e;
    --bg: #f5f7fa;
    --bg3: #ffffff;
    --text: #1a1a2e;
    --text-dim: #5a6480;
    --card-border: rgba(0,102,204,0.15);
    --glow: 0 4px 24px rgba(0,102,204,0.12);
  }}
  [data-theme="dark"] {{
    --primary: #00d4ff;
    --secondary: #7b2ff7;
    --bg: #0a0a0f;
    --bg3: #1a1a28;
    --text: #e8e8f0;
    --text-dim: #8888aa;
    --card-border: rgba(0,212,255,0.15);
    --glow: 0 0 20px rgba(0,212,255,0.3);
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--text); font-family:'Segoe UI',system-ui,sans-serif; overflow-x:hidden; line-height:1.6; transition: background 0.3s, color 0.3s; }}
  body::before {{ content:''; position:fixed; inset:0; background: radial-gradient(ellipse at 20% 20%, rgba(107,33,232,0.05) 0%, transparent 50%), radial-gradient(ellipse at 80% 80%, rgba(0,102,204,0.05) 0%, transparent 50%); pointer-events:none; z-index:0; }}
  body::after {{ content:''; position:fixed; inset:0; background-image: linear-gradient(rgba(0,102,204,0.04) 1px,transparent 1px), linear-gradient(90deg,rgba(0,102,204,0.04) 1px,transparent 1px); background-size:60px 60px; pointer-events:none; z-index:0; }}
  [data-theme="dark"] body::before {{ background: radial-gradient(ellipse at 20% 20%, rgba(123,47,247,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 80%, rgba(0,212,255,0.06) 0%, transparent 50%); }}
  [data-theme="dark"] body::after {{ background-image: linear-gradient(rgba(0,212,255,0.03) 1px,transparent 1px), linear-gradient(90deg,rgba(0,212,255,0.03) 1px,transparent 1px); background-size:60px 60px; }}
  .container {{ max-width:1000px; margin:0 auto; padding:0 24px; position:relative; z-index:1; }}
  .toolbar {{ position:fixed; top:20px; right:20px; z-index:1000; display:flex; gap:8px; }}
  .toolbar-btn {{ display:flex; align-items:center; gap:6px; padding:8px 16px; border-radius:50px; border:1px solid var(--card-border); background:var(--bg3); color:var(--text); font-size:13px; font-weight:500; cursor:pointer; transition:all 0.25s; box-shadow:0 2px 12px rgba(0,0,0,0.08); }}
  .toolbar-btn:hover {{ border-color:var(--primary); color:var(--primary); box-shadow:var(--glow); }}
  .hero {{ min-height:100vh; display:flex; align-items:center; justify-content:center; text-align:center; padding:60px 24px; position:relative; }}
  .hero-inner {{ max-width:700px; }}
  .hero-badge {{ display:inline-block; background:linear-gradient(135deg,rgba(0,102,204,0.1),rgba(107,33,232,0.1)); border:1px solid rgba(0,102,204,0.3); border-radius:50px; padding:6px 20px; font-size:12px; letter-spacing:3px; text-transform:uppercase; color:var(--primary); margin-bottom:28px; opacity:0; animation:fadeUp 0.8s ease 0.2s forwards; }}
  .hero-name {{ font-size:clamp(42px,8vw,80px); font-weight:800; line-height:1.1; background:linear-gradient(135deg,#1a1a2e 0%,var(--primary) 50%,var(--secondary) 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; opacity:0; animation:fadeUp 0.8s ease 0.4s forwards; margin-bottom:8px; }}
  [data-theme="dark"] .hero-name {{ background:linear-gradient(135deg,#fff 0%,var(--primary) 50%,var(--secondary) 100%); -webkit-background-clip:text; background-clip:text; }}
  .hero-name-cn {{ font-size:clamp(20px,4vw,32px); font-weight:300; color:var(--text-dim); opacity:0; animation:fadeUp 0.8s ease 0.5s forwards; margin-bottom:24px; }}
  .hero-title {{ font-size:clamp(16px,3vw,22px); color:var(--primary); font-weight:400; opacity:0; animation:fadeUp 0.8s ease 0.6s forwards; margin-bottom:32px; }}
  .hero-contacts {{ display:flex; gap:20px; justify-content:center; flex-wrap:wrap; opacity:0; animation:fadeUp 0.8s ease 0.8s forwards; }}
  .contact-item {{ display:flex; align-items:center; gap:8px; color:var(--text-dim); font-size:14px; padding:8px 16px; border:1px solid rgba(0,0,0,0.08); border-radius:8px; background:rgba(0,0,0,0.02); transition:all 0.3s; }}
  [data-theme="dark"] .contact-item {{ border-color:rgba(255,255,255,0.08); background:rgba(255,255,255,0.03); }}
  .contact-item:hover {{ border-color:var(--primary); color:var(--primary); }}
  .scroll-hint {{ position:absolute; bottom:40px; left:50%; transform:translateX(-50%); display:flex; flex-direction:column; align-items:center; gap:8px; color:var(--text-dim); font-size:12px; letter-spacing:2px; opacity:0; animation:fadeIn 1s ease 1.5s forwards; }}
  .scroll-arrow {{ width:20px; height:20px; border-right:2px solid var(--primary); border-bottom:2px solid var(--primary); transform:rotate(45deg); animation:bounce 1.5s ease infinite; }}
  section {{ padding:80px 0; }}
  .section-header {{ display:flex; align-items:center; gap:16px; margin-bottom:48px; }}
  .section-number {{ font-size:12px; color:var(--primary); letter-spacing:3px; font-weight:600; }}
  .section-title {{ font-size:clamp(24px,4vw,36px); font-weight:700; background:linear-gradient(135deg,#1a1a2e,var(--text-dim)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
  [data-theme="dark"] .section-title {{ background:linear-gradient(135deg,#fff,var(--text-dim)); -webkit-background-clip:text; background-clip:text; }}
  .section-line {{ flex:1; height:1px; background:linear-gradient(90deg,rgba(0,102,204,0.4),transparent); }}
  .skills-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; }}
  .skill-card {{ background:var(--bg3); border:1px solid var(--card-border); border-radius:16px; padding:24px; transition:all 0.4s; opacity:0; transform:translateY(30px); box-shadow:0 2px 12px rgba(0,0,0,0.06); }}
  .skill-card.visible {{ opacity:1; transform:translateY(0); }}
  .skill-card:hover {{ border-color:var(--primary); box-shadow:var(--glow); transform:translateY(-4px); }}
  .skill-icon {{ font-size:28px; margin-bottom:12px; }}
  .skill-card h3 {{ font-size:15px; font-weight:600; color:var(--primary); margin-bottom:8px; }}
  .skill-card p {{ font-size:13px; color:var(--text-dim); line-height:1.6; }}
  .stats-row {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:20px; margin-bottom:60px; }}
  .stat-card {{ background:var(--bg3); border:1px solid var(--card-border); border-radius:16px; padding:28px 20px; text-align:center; opacity:0; transform:scale(0.9); transition:all 0.5s; box-shadow:0 2px 12px rgba(0,0,0,0.06); }}
  .stat-card.visible {{ opacity:1; transform:scale(1); }}
  .stat-card:hover {{ border-color:var(--primary); box-shadow:var(--glow); }}
  .stat-number {{ font-size:42px; font-weight:800; background:linear-gradient(135deg,var(--primary),var(--secondary)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; line-height:1; margin-bottom:8px; }}
  .stat-label {{ font-size:12px; color:var(--text-dim); letter-spacing:1px; text-transform:uppercase; }}
  .timeline {{ position:relative; padding-left:32px; }}
  .timeline::before {{ content:''; position:absolute; left:0; top:0; bottom:0; width:2px; background:linear-gradient(180deg,var(--primary),var(--secondary),transparent); }}
  .timeline-item {{ position:relative; margin-bottom:48px; opacity:0; transform:translateX(-20px); transition:all 0.6s ease; }}
  .timeline-item.visible {{ opacity:1; transform:translateX(0); }}
  .timeline-dot {{ position:absolute; left:-39px; top:6px; width:14px; height:14px; border-radius:50%; background:var(--primary); border:2px solid var(--bg); box-shadow:0 0 10px var(--primary); animation:pulse 2s ease infinite; }}
  .timeline-card {{ background:var(--bg3); border:1px solid var(--card-border); border-radius:16px; padding:28px; transition:all 0.3s; box-shadow:0 2px 12px rgba(0,0,0,0.06); }}
  .timeline-card:hover {{ border-color:rgba(0,102,204,0.4); box-shadow:var(--glow); }}
  .timeline-meta {{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:12px; }}
  .timeline-company {{ font-size:13px; font-weight:600; color:var(--primary); background:rgba(0,102,204,0.1); padding:3px 12px; border-radius:20px; border:1px solid rgba(0,102,204,0.2); }}
  [data-theme="dark"] .timeline-company {{ background:rgba(0,212,255,0.1); border-color:rgba(0,212,255,0.2); }}
  .timeline-period {{ font-size:12px; color:var(--text-dim); letter-spacing:1px; }}
  .timeline-card h3 {{ font-size:18px; font-weight:700; color:var(--text); margin-bottom:10px; }}
  .timeline-card p {{ font-size:14px; color:var(--text-dim); line-height:1.7; margin-bottom:14px; }}
  .tech-tags {{ display:flex; flex-wrap:wrap; gap:8px; }}
  .tag {{ font-size:11px; padding:4px 12px; border-radius:20px; font-weight:500; }}
  .tag-platform {{ background:rgba(123,47,247,0.1); border:1px solid rgba(123,47,247,0.25); color:#7b2ff7; }}
  [data-theme="dark"] .tag-platform {{ color:#b57bff; }}
  .tag-lang {{ background:rgba(0,102,204,0.1); border:1px solid rgba(0,102,204,0.2); color:var(--primary); }}
  .tag-framework {{ background:rgba(229,62,62,0.08); border:1px solid rgba(229,62,62,0.2); color:var(--accent); }}
  .edu-card {{ background:var(--bg3); border:1px solid var(--card-border); border-radius:16px; padding:32px; display:flex; align-items:center; gap:24px; opacity:0; transform:translateY(20px); transition:all 0.6s; box-shadow:0 2px 12px rgba(0,0,0,0.06); }}
  .edu-card.visible {{ opacity:1; transform:translateY(0); }}
  .edu-icon {{ font-size:48px; flex-shrink:0; }}
  .edu-card h3 {{ font-size:20px; font-weight:700; color:var(--text); margin-bottom:6px; }}
  .edu-card p {{ color:var(--text-dim); font-size:14px; }}
  footer {{ text-align:center; padding:60px 24px; color:var(--text-dim); font-size:13px; border-top:1px solid rgba(0,0,0,0.06); }}
  [data-theme="dark"] footer {{ border-top-color:rgba(255,255,255,0.05); }}
  footer span {{ color:var(--primary); }}
  .skill-card:nth-child(1){{transition-delay:0.0s}}.skill-card:nth-child(2){{transition-delay:0.1s}}.skill-card:nth-child(3){{transition-delay:0.2s}}.skill-card:nth-child(4){{transition-delay:0.3s}}.skill-card:nth-child(5){{transition-delay:0.4s}}.skill-card:nth-child(6){{transition-delay:0.5s}}
  .stat-card:nth-child(1){{transition-delay:0.0s}}.stat-card:nth-child(2){{transition-delay:0.1s}}.stat-card:nth-child(3){{transition-delay:0.2s}}.stat-card:nth-child(4){{transition-delay:0.3s}}
  @keyframes fadeUp {{ from{{opacity:0;transform:translateY(30px)}} to{{opacity:1;transform:translateY(0)}} }}
  @keyframes fadeIn {{ from{{opacity:0}} to{{opacity:1}} }}
  @keyframes bounce {{ 0%,100%{{transform:rotate(45deg) translateY(0)}} 50%{{transform:rotate(45deg) translateY(6px)}} }}
  @keyframes pulse {{ 0%,100%{{box-shadow:0 0 6px var(--primary)}} 50%{{box-shadow:0 0 14px var(--primary),0 0 28px rgba(0,102,204,0.25)}} }}
</style>
</head>
<body>
<div class="toolbar">
  <button class="toolbar-btn" onclick="toggleLang()"><span>🌐</span><span id="langLabel">中文</span></button>
  <button class="toolbar-btn" onclick="toggleTheme()"><span id="themeIcon">🌙</span><span id="themeLabel">Dark</span></button>
</div>

<section class="hero">
  <div class="hero-inner">
    <div class="hero-badge" data-en="Full-Stack Mobile Engineer" data-zh="全栈移动端工程师">Full-Stack Mobile Engineer</div>
    <h1 class="hero-name">Andrew Wang</h1>
    <div class="hero-name-cn">汪奇伟</div>
    <div class="hero-title" data-en="15+ Years · Flutter · iOS · React Native · AI-Driven Development" data-zh="15年以上 · Flutter · iOS · React Native · AI驱动开发">15+ Years · Flutter · iOS · React Native · AI-Driven Development</div>
    <div class="hero-contacts">{contacts}</div>
  </div>
  <div class="scroll-hint"><span data-en="SCROLL" data-zh="滚动">SCROLL</span><div class="scroll-arrow"></div></div>
</section>

<div class="container">
  <div class="stats-row">
    <div class="stat-card"><div class="stat-number">15+</div><div class="stat-label" data-en="Years Experience" data-zh="年从业经验">Years Experience</div></div>
    <div class="stat-card"><div class="stat-number">13</div><div class="stat-label" data-en="Major Projects" data-zh="重点项目">Major Projects</div></div>
    <div class="stat-card"><div class="stat-number">6</div><div class="stat-label" data-en="Companies" data-zh="就职公司">Companies</div></div>
    <div class="stat-card"><div class="stat-number">8+</div><div class="stat-label" data-en="Tech Stacks" data-zh="技术栈">Tech Stacks</div></div>
  </div>
</div>

<section>
  <div class="container">
    <div class="section-header">
      <span class="section-number">01</span>
      <h2 class="section-title" data-en="Core Skills" data-zh="核心技能">Core Skills</h2>
      <div class="section-line"></div>
    </div>
    <div class="skills-grid">{skills}</div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-header">
      <span class="section-number">02</span>
      <h2 class="section-title" data-en="Project Experience" data-zh="项目经历">Project Experience</h2>
      <div class="section-line"></div>
    </div>
    <div class="timeline">{projects}</div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-header">
      <span class="section-number">03</span>
      <h2 class="section-title" data-en="Early Career" data-zh="早期经历">Early Career</h2>
      <div class="section-line"></div>
    </div>
    <div class="timeline">{early}</div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-header">
      <span class="section-number">04</span>
      <h2 class="section-title" data-en="Education" data-zh="教育背景">Education</h2>
      <div class="section-line"></div>
    </div>
    <div class="edu-card">
      <div class="edu-icon">🎓</div>
      <div>
        <h3 data-en="University of Electronic Science and Technology of China (UESTC)" data-zh="电子科技大学（UESTC）">{edu_school}</h3>
        <p data-en="Bachelor's Degree · Software Engineering · Chengdu, China" data-zh="本科 · 软件工程 · 中国成都">{edu_detail}</p>
      </div>
    </div>
  </div>
</section>

<footer>
  <p>Andrew Wang 汪奇伟 &nbsp;·&nbsp; <span data-en="15+ Years Full-Stack Mobile Engineer" data-zh="15年以上全栈移动端工程师">15+ Years Full-Stack Mobile Engineer</span> &nbsp;·&nbsp; IBM · Flutter · iOS · React Native</p>
</footer>

<script>
  const obs = new IntersectionObserver(e => e.forEach(x => x.isIntersecting && x.target.classList.add('visible')), {{threshold:0.1,rootMargin:'0px 0px -40px 0px'}});
  document.querySelectorAll('.skill-card,.timeline-item,.stat-card,.edu-card').forEach(el => obs.observe(el));

  const cObs = new IntersectionObserver(e => e.forEach(x => {{
    if (!x.isIntersecting) return;
    const el = x.target.querySelector('.stat-number');
    const num = parseInt(el.textContent), suf = el.textContent.replace(/[0-9]/g,'');
    let s=0; const step=ts=>{{ if(!s)s=ts; const p=Math.min((ts-s)/1500,1),e2=1-Math.pow(1-p,3); el.textContent=Math.floor(e2*num)+suf; if(p<1)requestAnimationFrame(step); }}; requestAnimationFrame(step);
    cObs.unobserve(x.target);
  }}), {{threshold:0.5}});
  document.querySelectorAll('.stat-card').forEach(el => cObs.observe(el));

  let lang='en';
  function toggleLang(){{
    lang = lang==='en'?'zh':'en';
    document.getElementById('langLabel').textContent = lang==='zh'?'English':'中文';
    document.querySelectorAll('[data-en][data-zh]').forEach(el => el.textContent = lang==='zh'?el.dataset.zh:el.dataset.en);
  }}

  let theme='light';
  function toggleTheme(){{
    theme = theme==='light'?'dark':'light';
    document.documentElement.setAttribute('data-theme', theme==='dark'?'dark':'');
    document.getElementById('themeIcon').textContent = theme==='dark'?'☀️':'🌙';
    document.getElementById('themeLabel').textContent = theme==='dark'?'Light':'Dark';
  }}
</script>
</body>
</html>"""

if __name__ == '__main__':
    build('resume.md', 'index.html')

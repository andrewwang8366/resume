#!/usr/bin/env python3
"""Parse resume.en.md + resume.zh.md → i18n.js"""
import re, json

def parse_md(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    data = {
        'name': '', 'subtitle': '', 'contacts': [],
        'summary': '', 'skills': [], 'projects': [], 'early': [],
        'education': {'school': '', 'detail': ''}
    }

    m = re.search(r'^# (.+)', content, re.M)
    if m: data['name'] = m.group(1).strip()

    m = re.search(r'^\*\*(.+?)\*\*', content, re.M)
    if m: data['subtitle'] = m.group(1).strip()

    for c in re.findall(r'^- (.+)', content[:600], re.M):
        data['contacts'].append(c.strip())

    sm = re.search(r'## (?:Summary|简介)\s*\n\n(.+?)\n\n---', content, re.S)
    if sm: data['summary'] = sm.group(1).strip()

    sk = re.search(r'## (?:Core Skills|核心技能)\s*\n(.*?)---', content, re.S)
    if sk:
        for line in sk.group(1).strip().split('\n'):
            m2 = re.match(r'- \*\*(.+?)\*\* — (.+)', line.strip())
            if m2:
                # Strip any remaining markdown bold markers from desc
                desc = re.sub(r'\*\*(.+?)\*\*', r'\1', m2.group(2))
                data['skills'].append({'name': m2.group(1), 'desc': desc})

    def parse_section(text):
        items = []
        for block in re.split(r'\n### ', '\n' + text):
            block = block.strip()
            if not block:
                continue
            lines = block.split('\n')
            title = lines[0].strip()
            company, period, tags, desc_parts = '', '', [], []
            for line in lines[1:]:
                line = line.strip()
                if not line or line == '---':
                    continue
                meta = re.match(r'\*\*(.+?) · (.+?)\*\*', line)
                if meta:
                    company, period = meta.group(1), meta.group(2)
                elif re.match(r'^`', line):
                    tags = re.findall(r'`([^`]+)`', line)
                else:
                    desc_parts.append(line)
            items.append({
                'title': title, 'company': company,
                'period': period, 'tags': tags,
                'desc': ' '.join(desc_parts).strip()
            })
        return items

    proj_m = re.search(
        r'## (?:Project Experience|项目经历)\s*\n(.*?)## (?:Early Career|早期经历)',
        content, re.S)
    if proj_m:
        data['projects'] = parse_section(proj_m.group(1))

    early_m = re.search(
        r'## (?:Early Career|早期经历)\s*\n(.*?)## (?:Education|教育背景)',
        content, re.S)
    if early_m:
        data['early'] = parse_section(early_m.group(1))

    edu_m = re.search(r'## (?:Education|教育背景)\s*\n\n\*\*(.+?)\*\*\n(.+)', content)
    if edu_m:
        data['education'] = {
            'school': edu_m.group(1).strip(),
            'detail': edu_m.group(2).strip()
        }

    return data


if __name__ == '__main__':
    en = parse_md('resume.en.md')
    zh = parse_md('resume.zh.md')
    with open('i18n.js', 'w', encoding='utf-8') as f:
        f.write('const I18N = ' + json.dumps({'en': en, 'zh': zh}, ensure_ascii=False, indent=2) + ';\n')
    print('Built i18n.js')

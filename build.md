# 简历更新指南

## 日常更新流程

1. **编辑简历内容**
   - 英文：编辑 `resume.en.md`
   - 中文：编辑 `resume.zh.md`

2. **本地构建（可选，用于本地预览）**
   ```bash
   cd /Users/wangqiwei/Program/Resume
   python3 build.py
   ```
   这会重新生成 `i18n.js`，然后直接用浏览器打开 `index.html` 预览。

3. **推送到 GitHub（自动部署）**
   ```bash
   git add resume.en.md resume.zh.md
   git commit -m "update: 更新简历内容"
   git push
   ```
   推送后，GitHub Actions 会自动：
   - 运行 `build.py` 生成 `i18n.js`
   - 将最新内容部署到 GitHub Pages

4. **查看线上效果**
   访问：https://andrewwang8366.github.io/resume/

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `resume.en.md` | 英文简历源文件，**日常只需改这个** |
| `resume.zh.md` | 中文简历源文件，**日常只需改这个** |
| `build.py` | 解析两个 md 文件，生成 `i18n.js` |
| `i18n.js` | 自动生成，不要手动编辑 |
| `index.html` | 网页模板，一般不需要改 |
| `.github/workflows/deploy.yml` | GitHub Actions 自动部署配置 |

---

## md 文件格式说明

### 基本结构
```markdown
# 姓名

**职位头衔**

- 📱 电话
- ✉️ 邮箱
- 🎓 学校

---

## 简介 / Summary

一段话简介

---

## 核心技能 / Core Skills

- **技能名** — 技能描述

---

## 项目经历 / Project Experience

### 项目名称

**公司 · 时间段**
`技术标签1` `技术标签2`

项目描述文字

---

## 早期经历 / Early Career

（同上格式）

---

## 教育背景 / Education

**学校名称**
学位 · 专业 · 地点
```

### 注意事项
- 每个项目之间用 `---` 分隔
- 技术标签用反引号包裹：`` `Flutter` ``
- 公司和时间用 `**公司 · 时间**` 格式
- 不要在描述文字里用 `**加粗**`，会被自动去掉

---

## 修改网页样式

如果需要调整网页的视觉效果（颜色、字体、动画等），编辑 `index.html`，然后直接推送即可。

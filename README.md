# Reasonable Or Not / 手机推荐系统

A Django-based phone recommendation engine that matches user preferences against a database of 300+ Chinese smartphone models using **cosine similarity**.

一个基于 Django 的手机推荐引擎，通过**余弦相似度算法**，将用户偏好与 300+ 款国产手机数据库进行匹配。

---

## Project Overview / 项目概述

**Reasonable Or Not** transforms a classroom recommender concept into a polished web application. Users fill out a preference form (budget, performance, charging speed, screen size, storage, battery, camera), and the system returns the best-matched phone with a similarity score and alternatives.

**Reasonable Or Not** 将课堂作业中的推荐概念打造为完整的 Web 应用。用户填写偏好表单（预算、性能、充电速度、屏幕大小、存储、电池、相机），系统返回最佳匹配机型、相似度评分及备选方案。

---

## Tech Stack / 技术栈

| Layer | Technology |
|-------|------------|
| Backend | Django 3.2 / Python 3.11 |
| Database | PostgreSQL (Railway) / SQLite (local) |
| WSGI Server | Gunicorn |
| Static Files | WhiteNoise |
| Frontend | Vanilla CSS (Apple-style design system) |
| Algorithm | Cosine similarity on normalized feature vectors |

---

## Recommendation Algorithm / 推荐算法

The system converts both user preferences and phone specs into normalized feature vectors, then computes **cosine similarity** between them:

系统将用户偏好和手机规格分别转换为归一化特征向量，计算二者之间的**余弦相似度**：

```
cos(θ) = (A · B) / (|A| × |B|)
```

Feature dimensions / 特征维度：Budget · Performance · Charging · Screen Size · Storage · Battery · Camera

---

## Pages / 页面

| Route | Description |
|-------|-------------|
| `/user/index` | Landing page with featured phones / 首页展示精选机型 |
| `/user/register` | Account registration / 用户注册 |
| `/user/login` | User login / 用户登录 |
| `/user/logout` | Session logout / 登出 |
| `/user/requirement` | Multi-step preference form / 偏好表单 |
| `/user/recommend` | Best match + alternatives / 最佳匹配及备选 |
| `/user/result` | Value ranking + methodology / 性价比排名与方法论 |

---

## Local Setup / 本地运行

```bash
# 1. Clone / 克隆
git clone https://github.com/lennney/ReasonableOrNot.git
cd ReasonableOrNot

# 2. Virtual environment / 虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies / 安装依赖
pip install -r requirements.txt

# 4. Database migrations / 数据库迁移
python manage.py migrate

# 5. Import phone data (optional) / 导入手机数据（非必须）
python manage.py import_phones

# 6. Run development server / 启动开发服务器
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

---

## Production Deployment / 生产部署

The project is configured for **Railway** with PostgreSQL:

```bash
# Key environment variables / 关键环境变量
DATABASE_URL=postgres://user:password@host:port/dbname
DEBUG=False
```

Static files are served by WhiteNoise without `collectstatic`.

---

## Project Structure / 项目结构

```
ReasonableOrNot/
├── login/              # Django project settings / 项目配置
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
├── user/               # Main app / 主应用
│   ├── models.py       # User & Phone models
│   ├── views.py        # All page logic + cosine similarity
│   ├── urls.py
│   ├── admin.py
│   └── management/commands/import_phones.py
├── templates/user/     # HTML templates
├── static/css/         # Stylesheets
├── phones_data.csv     # Phone database (300+ models)
└── requirements.txt
```

---

## Database Schema / 数据库结构

**User** — `username`, `password` (MD5+salt), `email`

**Phone** — `brand`, `model`, `price`, `cpu`, `ram`, `rom`, `charging`, `battery`, `screen_refresh_rate`, `screen_resolution`, `weight`, `front_camera`, `rear_camera`, `screen_size`

---

## Why This Project / 项目价值

- Demonstrates **end-to-end web development** from database design to UI
- Shows **algorithmic thinking** (cosine similarity, vector normalization)
- Portfolio-ready **Apple-style frontend** with scroll animations and cursor glow
- Clean Django architecture with **separation of concerns**
- Handles **Chinese smartphone market data** (300+ real models)

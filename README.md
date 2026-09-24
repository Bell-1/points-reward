# 积分奖励平台

家长管理积分、孩子完成任务赚取积分的积分奖励系统。支持任务审核、积分管理、商品兑换等功能。

## 功能特性

### 家长端
- **数据统计** - 实时查看孩子积分、任务完成情况
- **任务管理** - 创建/编辑/删除任务，支持每日/每周/每月/次任务四种周期
- **任务审核** - 审批孩子提交的任务完成记录
- **商品管理** - 上架/下架商品，支持积分兑换
- **兑换审核** - 审批孩子的商品兑换申请（可选需审核模式）
- **孩子管理** - 添加/编辑孩子信息，单独调整积分
- **积分管理** - 查看所有积分变动记录，支持手动增减积分

### 孩子端
- **任务中心** - 查看并完成任务，获得积分奖励
- **积分商店** - 使用积分兑换商品
- **兑换记录** - 查看兑换申请状态（待审核/已通过/已驳回）
- **积分明细** - 查看收支记录

## 技术栈

**后端**
- FastAPI + SQLAlchemy + SQLite
- Python 3.13

**前端**
- Vue 3 + Vite + Pinia
- 移动端优先设计，支持 PWA（iPad 可添加到主屏幕）

**部署**
- Docker Compose 一键启动前后端

## 快速启动

### 方式一：Docker（推荐）

```bash
./start.sh
```

- 后端：http://localhost:8000
- 前端：http://localhost:7888

停止服务：
```bash
./stop.sh
```

### 方式二：本地开发

**后端**
```bash
cd backend  # 或直接 cd /
uvicorn app.main:app --reload --port 8000
```

**前端**
```bash
cd frontend
pnpm install
pnpm dev
```

## 项目结构

```
points-reward/
├── app/                    # 后端代码
│   ├── api/               # API 路由
│   │   ├── admin.py       # 管理员接口
│   │   ├── auth.py        # 登录认证
│   │   └── child.py       # 孩子端接口
│   ├── models/            # 数据库模型
│   ├── schemas/           # Pydantic 模型
│   └── utils/             # 工具函数
├── frontend/              # 前端代码
│   └── src/
│       ├── api/           # API 调用
│       ├── layouts/        # 布局组件
│       ├── router/         # 路由配置
│       ├── stores/         # Pinia 状态管理
│       └── views/          # 页面组件
├── docker-compose.yml      # Docker 配置
└── start.sh               # 启动脚本
```

## 默认账号

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | admin | admin123 |
| 孩子 | child1 | 1234 |

## 接口文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

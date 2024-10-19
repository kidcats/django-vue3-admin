# 安全漏洞简报系统 - 软件开发设计文档

## 1. 系统概述

安全漏洞简报系统是一个用于管理和生成安全漏洞相关报告的综合平台。该系统包含多个核心模块，如简报管理、任务管理、模板管理和系统管理等，旨在提供高效、安全的漏洞报告生成和分发服务。

## 2. 系统架构

该系统采用前后端分离的架构：

- 前端：使用现代JavaScript框架（Vue.js）
- 后端：采用RESTful API设计，使用适当的后端框架（Django）
- 数据库：关系型数据库（MySQL）
- 任务队列：Celery用于处理异步任务和定时任务

包含简报管理、任务管理、模板管理、系统管理4个模块。

下面将分模块描述：

## 3. 模块设计

### 3.1 简报管理模块

#### 功能分析：

- 简报的创建、编辑、删除和查看
- 简报的搜索和筛选，支持根据日期过滤
- 简报的邮件历史记录查看
- 批量操作功能

#### 数据模型：

**简报（Report）**
- id: 主键
- title: 标题（字符串）
- type: 类型（枚举：日报、周报、月报、季报、年报、其它）
- summary: 摘要（文本）
- content: 内容（富文本）
- created_at: 创建时间（日期时间）
- report_date: 简报日期（日期）
- creator_id: 创建者ID（外键关联用户表）

**邮件发送记录（EmailSendRecord）**
- id: 主键
- report_id: 关联简报ID（外键）
- sent_at: 发送时间（日期时间）
- recipients: 接收者（文本，存储邮件地址列表）
- status: 发送状态（枚举：成功、失败）

#### 接口设计：

1. **GET /api/reports**
   - 功能：获取简报列表
   - 参数：
     - page: 页码
     - per_page: 每页数量
     - title: 标题搜索
     - type: 简报类型
     - start_date: 开始日期
     - end_date: 结束日期
   - 返回：简报列表及分页信息
  ```json
  {
  "current_page": 1,
  "per_page": 10,
  "total_pages": 5,
  "total_items": 50,
  "data": [
    {
      "id": 1,
      "title": "2023年安全漏洞周报",
      "type": "周报",
      "summary": "本周发现5个新的安全漏洞...",
      "content": "<p>详细内容...</p>",
      "created_at": "2023-04-25T10:30:00Z",
      "report_date": "2023-04-24",
      "creator_id": 3
    },
    // 更多简报
  ]
}
  ```

2. **POST /api/reports**
   - 功能：创建新简报
   - 参数：简报详细信息（title, type, summary, content, report_date）
   - 返回：创建的简报详情
  请求示例
```json
   {
  "title": "2023年第四季度安全漏洞月报",
  "type": "月报",
  "summary": "第四季度共发现15个安全漏洞，主要集中在...",
  "content": "<h1>第四季度安全漏洞概述</h1><p>详细内容...</p>",
  "report_date": "2023-12-31"
}
   ```
   响应
  ```json
  {
  "id": 51,
  "title": "2023年第四季度安全漏洞月报",
  "type": "月报",
  "summary": "第四季度共发现15个安全漏洞，主要集中在...",
  "content": "<h1>第四季度安全漏洞概述</h1><p>详细内容...</p>",
  "created_at": "2023-12-01T09:00:00Z",
  "report_date": "2023-12-31",
  "creator_id": 5
}
  ```
1. **GET /api/reports/<id>**
   - 功能：获取特定简报详情
   - 参数：简报ID
   - 返回：简报详细信息
  ```json
  {
  "id": 1,
  "title": "2023年安全漏洞周报",
  "type": "周报",
  "summary": "本周发现5个新的安全漏洞...",
  "content": "<p>详细内容...</p>",
  "created_at": "2023-04-25T10:30:00Z",
  "report_date": "2023-04-24",
  "creator_id": 3
}
  ```
1. **PUT /api/reports/<id>**
   - 功能：更新简报信息
   - 参数：简报ID，更新的字段
   - 返回：更新后的简报详情
请求
  ```json
  {
  "title": "2023年安全漏洞周报（更新版）",
  "summary": "更新后的摘要内容...",
  "content": "<p>更新后的详细内容...</p>"
}
  ```
响应
  ```json
  {
  "id": 1,
  "title": "2023年安全漏洞周报（更新版）",
  "type": "周报",
  "summary": "更新后的摘要内容...",
  "content": "<p>更新后的详细内容...</p>",
  "created_at": "2023-04-25T10:30:00Z",
  "report_date": "2023-04-24",
  "creator_id": 3,
  "updated_at": "2023-04-26T14:45:00Z"
}
  ```
1. **DELETE /api/reports/<id>**
   - 功能：删除简报
   - 参数：简报ID
   - 返回：操作结果
  ```json
  {
  "message": "简报已成功删除。"
}
  ```
1. **POST /api/reports/<id>/send**
   - 功能：发送简报邮件
   - 参数：简报ID，接收者列表
   - 返回：发送结果
  请求
  ```json
  {
  "recipients": ["user1@example.com", "user2@example.com"]
}
  ```
  响应
  ```json
  {
  "report_id": 1,
  "sent_at": "2023-04-26T15:00:00Z",
  "recipients": ["user1@example.com", "user2@example.com"],
  "status": "成功"
}
  ```
1. **GET /api/reports/<id>/email-history**
   - 功能：获取简报的邮件发送历史
   - 参数：简报ID
   - 返回：邮件发送记录列表
  ```json
  {
  "report_id": 1,
  "email_history": [
    {
      "id": 1001,
      "sent_at": "2023-04-26T15:00:00Z",
      "recipients": ["user1@example.com", "user2@example.com"],
      "status": "成功"
    },
    {
      "id": 1002,
      "sent_at": "2023-05-03T15:00:00Z",
      "recipients": ["user3@example.com"],
      "status": "失败"
    }
    // 更多发送记录
  ]
}
  ```
### 3.2 任务管理模块

#### 功能分析：

- 定时任务的创建、编辑、删除和查看
- 任务日志的查看和管理，可以再次执行
- 中间表数据的展示和管理

#### 数据模型：

**定时任务（ScheduledTask）**
- id: 主键
- name: 任务名称（字符串）
- frequency: 执行频率（字符串，可以用于在Celery中创建任务）
- created_at: 创建时间（日期时间）
- updated_at: 更新时间（日期时间）
- status: 状态（枚举：运行中、暂停）
- template: 关联的简报模板（外键）
- 操作：枚举（编辑、停止、删除）

**任务日志（TaskLog）**
- id: 主键
- job_id: 任务ID（字符串）
- task_name: 任务名称（字符串）
- start_time: 开始时间（日期时间）
- end_time: 结束时间（日期时间）
- result: 执行结果（枚举：成功、失败、执行中）
- details: 详细信息（JSON，包含job_id,任务名称，开始时间，结束时间，运行参数，执行结果，错误信息）
- 操作：枚举（详情、再次执行、删除）

**中间数据（IntermediateData）**
- id: 主键
- date: 日期（日期）
- internal_attacks: 内网攻击数（整数）
- external_attacks: 外网攻击数（整数）
- other_metrics: 其他相关指标（JSON）
- job_id: 关联的任务ID（外键）

#### 接口设计：

1. **GET /api/tasks**
   - 功能：获取定时任务列表
   - 参数：
     - page: 页码
     - per_page: 每页数量
     - name: 任务名称搜索
   - 返回：定时任务列表及分页信息
   - GET /api/reports?page=1&per_page=10&title=安全漏洞&type=周报&start_date=2023-01-01&end_date=2023-12-31
  ```json
  {
  "current_page": 1,
  "per_page": 10,
  "total_pages": 2,
  "total_items": 15,
  "data": [
    {
      "id": 1,
      "name": "每日简报发送",
      "frequency": "0 9 * * *",  // Cron 表达式
      "created_at": "2023-01-10T08:00:00Z",
      "updated_at": "2023-04-20T12:00:00Z",
      "status": "运行中",
      "template": {
        "id": 2,
        "template_type": "日报",
        "template_name": "默认日报模板"
      },
      "操作": ["编辑", "停止", "删除"]
    },
    // 更多任务
  ]
}

  ```
2. **POST /api/tasks**
   - 功能：创建新定时任务
   - 参数：任务详细信息（name, frequency, template_id）
   - 返回：创建的任务详情
  请求
  ```json
{
  "name": "每周漏洞扫描",
  "frequency": "0 10 * * 1",  // 每周一上午10点
  "template_id": 3
}
  ```
  响应
  ```json
{
  "id": 16,
  "name": "每周漏洞扫描",
  "frequency": "0 10 * * 1",
  "created_at": "2023-05-01T09:00:00Z",
  "updated_at": "2023-05-01T09:00:00Z",
  "status": "运行中",
  "template": {
    "id": 3,
    "template_type": "周报",
    "template_name": "漏洞扫描周报模板"
  },
  "操作": ["编辑", "停止", "删除"]
}creator_id": 5
}
  ```
3. **PUT /api/tasks/<id>**
   - 功能：更新定时任务
   - 参数：任务ID，更新的字段
   - 返回：更新后的任务详情  
   - 
请求
  ```json
  {
  "name": "每日安全简报发送",
  "frequency": "0 8 * * *",  // 修改为每天上午8点
  "template_id": 4
}
  ```
  响应
  ```json
{
  "id": 1,
  "name": "每日安全简报发送",
  "frequency": "0 8 * * *",
  "created_at": "2023-01-10T08:00:00Z",
  "updated_at": "2023-05-02T10:30:00Z",
  "status": "运行中",
  "template": {
    "id": 4,
    "template_type": "日报",
    "template_name": "高级日报模板"
  },
  "操作": ["编辑", "停止", "删除"]
}
  ```
4. **DELETE /api/tasks/<id>**
   - 功能：删除定时任务
   - 参数：任务ID
   - 返回：操作结果
  ```json
{
  "message": "定时任务已成功删除。"
}
  ```

5. **PATCH /api/tasks/<id>/status**
   - 功能：更新任务状态（暂停/恢复）
   - 参数：任务ID，新状态
   - 返回：更新后的任务状态  
  请求  
```json
{
  "status": "暂停"
}
  ```
响应  
  ```json
  {
  "id": 1,
  "name": "每日安全简报发送",
  "frequency": "0 8 * * *",
  "status": "暂停",
  "updated_at": "2023-05-03T11:00:00Z"
}
  ```
6. **GET /api/task-logs**
   - 功能：获取任务日志列表
   - 参数：
     - page: 页码
     - per_page: 每页数量
     - task_name: 任务名称搜索
   - 返回：任务日志列表及分页信息
  ```json
  {
  "current_page": 1,
  "per_page": 10,
  "total_pages": 3,
  "total_items": 25,
  "data": [
    {
      "id": 2001,
      "job_id": "celery-task-123",
      "task_name": "每日安全简报发送",
      "start_time": "2023-04-25T08:00:00Z",
      "end_time": "2023-04-25T08:01:00Z",
      "result": "成功"
    },
    // 更多日志
  ]
}
  ```
7. **GET /api/task-logs/<job_id>**
   - 功能：获取特定任务的详细日志
   - 参数：job_id
   - 返回：详细日志信息
  ```json
  {
  "id": 2001,
  "job_id": "celery-task-123",
  "task_name": "每日安全简报发送",
  "start_time": "2023-04-25T08:00:00Z",
  "end_time": "2023-04-25T08:01:00Z",
  "result": "成功",
  "details": {
    "job_id": "celery-task-123",
    "task_name": "每日安全简报发送",
    "start_time": "2023-04-25T08:00:00Z",
    "end_time": "2023-04-25T08:01:00Z",
    "运行参数": {
      "report_date": "2023-04-25"
    },
    "执行结果": "简报发送成功。",
    "错误信息": null
  }
}
  ```
8. **POST /api/task-logs/<job_id>/rerun**
   - 功能：重新执行特定任务
   - 参数：job_id
   - 返回：重新执行的结果
  ```json
  {
  "job_id": "celery-task-124",
  "task_name": "每日安全简报发送",
  "status": "执行中"
}
  ```
9. **GET /api/intermediate-data**
   - 功能：获取中间数据列表
   - 参数：
     - start_date: 开始日期
     - end_date: 结束日期
   - 返回：中间数据列表
  ```json
  {
  "data": [
    {
      "id": 3001,
      "date": "2023-04-25",
      "internal_attacks": 10,
      "external_attacks": 5,
      "other_metrics": {
        "metric1": 100,
        "metric2": 200
      },
      "job_id": 1
    },
    // 更多中间数据
  ]
}
  ```
10. **PUT /api/intermediate-data/<id>**
    - 功能：更新中间数据
    - 参数：数据ID，更新的字段
    - 返回：更新后的数据详情  
  请求
  ```json
  {
  "internal_attacks": 12,
  "external_attacks": 6,
  "other_metrics": {
    "metric1": 110,
    "metric2": 210
  }
}
  ```
  响应
  ```json
  {
  "id": 3001,
  "date": "2023-04-25",
  "internal_attacks": 12,
  "external_attacks": 6,
  "other_metrics": {
    "metric1": 110,
    "metric2": 210
  },
  "job_id": 1
}
  ```
### 3.3 模板管理模块

#### 功能分析：

- 模板的创建、编辑、删除和查看
- 模板的搜索功能

#### 数据模型：

**模板（Template）**
- id: 主键
- template_type: 模板类型（枚举：日报、周报、月报、季报、年报）
- template_group: 模板分组（枚举：安全漏洞、钓鱼邮件）
- template_name: 模板名称（字符串）
- content: 模板内容（HTML/富文本）
- creator_id: 创建人ID（外键关联用户表）
- creator_name: 创建人姓名（外键关联用户表）
- create_datetime: 创建时间（日期时间）
- update_datetime: 最后更新时间（日期时间）

#### 接口设计：

1. **GET /api/templates/list**
   - 功能：获取模板列表
   - 参数：
     - page: 页码
     - per_page: 每页数量
     - name: 模板名称搜索
     - type: 模板类型
   - 返回：模板列表及分页信息
  ```json
  {
  "current_page": 1,
  "per_page": 10,
  "total_pages": 1,
  "total_items": 3,
  "data": [
    {
      "id": 2,
      "template_type": "日报",
      "template_name": "默认日报模板",
      "content": "<h1>日报模板</h1><p>内容...</p>",
      "creator_id": 3,
      "created_at": "2023-01-05T08:00:00Z",
      "updated_at": "2023-03-15T10:00:00Z"
    },
    // 更多模板
  ]
}
  ```
2. **POST /api/templates**
   - 功能：创建新模板
   - 参数：模板详细信息（template_type, template_name, content）
   - 返回：创建的模板详情

3. **GET /api/templates/<id>**
   - 功能：获取特定模板详情
   - 参数：模板ID
   - 返回：模板详细信息
  ```json
  {
  "id": 2,
  "template_type": "日报",
  "template_name": "默认日报模板",
  "content": "<h1>日报模板</h1><p>内容...</p>",
  "creator_id": 3,
  "created_at": "2023-01-05T08:00:00Z",
  "updated_at": "2023-03-15T10:00:00Z"
}
  ```
4. **PUT /api/templates/<id>**
   - 功能：更新模板信息
   - 参数：模板ID，更新的字段
   - 返回：更新后的模板详情  
请求
```json
  {
  "template_name": "默认日报模板（更新版）",
  "content": "<h1>更新后的日报模板</h1><p>新的内容...</p>"
  }
```
  响应
  ```json
  {
  "id": 2,
  "template_type": "日报",
  "template_name": "默认日报模板（更新版）",
  "content": "<h1>更新后的日报模板</h1><p>新的内容...</p>",
  "creator_id": 3,
  "created_at": "2023-01-05T08:00:00Z",
  "updated_at": "2023-05-04T11:30:00Z"
}
  ```
1. **DELETE /api/templates/<id>**
   - 功能：删除模板
   - 参数：模板ID
   - 返回：操作结果
  ```json
  {
  "message": "模板已成功删除。"
}
  ```
### 3.4 系统管理模块

#### 功能分析：

- 用户管理
- 角色管理
- 权限管理
- 菜单管理
- 邮件管理

本文档重点关注邮件管理子模块：

#### 数据模型：

**邮件配置（EmailConfiguration）**
- id: 主键
- report_type: 简报类型（枚举：日报、周报、月报、季报、年报）
- recipients: 邮件接收人列表（文本，多个邮箱用分号分隔）
- status: 启用状态（布尔值）
- creator_id: 创建人ID（外键关联用户表）
- created_at: 创建时间（日期时间）
- updated_at: 最后更新时间（日期时间）

#### 接口设计：

1. **GET /api/email-configs**
   - 功能：获取邮件配置列表
   - 参数：
     - page: 页码
     - per_page: 每页数量
   - 返回：邮件配置列表及分页信息
  ```json
  {
  "current_page": 1,
  "per_page": 10,
  "total_pages": 1,
  "total_items": 2,
  "data": [
    {
      "id": 1,
      "report_type": "周报",
      "recipients": "security-team@example.com; admin@example.com",
      "status": true,
      "creator_id": 2,
      "created_at": "2023-01-15T09:00:00Z",
      "updated_at": "2023-04-20T10:00:00Z"
    },
    {
      "id": 2,
      "report_type": "月报",
      "recipients": "manager@example.com",
      "status": false,
      "creator_id": 4,
      "created_at": "2023-02-10T11:00:00Z",
      "updated_at": "2023-03-22T14:00:00Z"
    }
  ]
}
  ```
2. **POST /api/email-configs**
   - 功能：创建新的邮件配置
   - 参数：邮件配置详情（report_type, recipients, status）
   - 返回：创建的邮件配置详情  
  请求
  ```json
  {
  "report_type": "日报",
  "recipients": "user1@example.com; user2@example.com",
  "status": true
}
  ```
  响应
```json
{
  "id": 3,
  "report_type": "日报",
  "recipients": "user1@example.com; user2@example.com",
  "status": true,
  "creator_id": 5,
  "created_at": "2023-05-05T10:00:00Z",
  "updated_at": "2023-05-05T10:00:00Z"
}
```
3. **PUT /api/email-configs/<id>**
   - 功能：更新邮件配置
   - 参数：配置ID，更新的字段
   - 返回：更新后的邮件配置详情
    请求
  ```json
  {
  "recipients": "security-team@example.com; admin@example.com; newuser@example.com",
  "status": false
}
  ```
  响应
  ```json
  {
  "id": 1,
  "report_type": "周报",
  "recipients": "security-team@example.com; admin@example.com; newuser@example.com",
  "status": false,
  "creator_id": 2,
  "created_at": "2023-01-15T09:00:00Z",
  "updated_at": "2023-05-06T12:00:00Z"
}
  ```
4. **DELETE /api/email-configs/<id>**
   - 功能：删除邮件配置
   - 参数：配置ID
   - 返回：操作结果  

  响应
  ```json
  {
  "message": "邮件配置已成功删除。"
}
  ```
1. **PATCH /api/email-configs/<id>/status**
   - 功能：更新邮件配置状态
   - 参数：配置ID，新状态
   - 返回：更新后的状态  
  请求
  ```json
  {
  "status": true
}
  ```
  响应
 ```json
 {
  "id": 1,
  "report_type": "周报",
  "recipients": "security-team@example.com; admin@example.com",
  "status": true,
  "updated_at": "2023-05-07T08:30:00Z"
}
  ```
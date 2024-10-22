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


## 4 task任务内容
### 4.1 数据查询  
- 输入：查询时间范围和查询语句
```Python
requestBody = {
  "query": query,
  "earliestTime": earliestTime,
  "latestTime": latestTime,
  "timezone": "Asia/Shanghai",
  "autoSort": False,
  "autoTruncate": True,
  "enableFieldsSummary": False,
  "enableTimeline": False,
  "enableSourceTrack": False,
  "forceUpdateSearch": False
}
repley = YanHuang.Search.commands(self=YanHuang.Search(),searchCommands=requestBody)
repley_events = repley['events']
```
- 输出：查询结果
### 4.2 数据处理
##### 4.2.1 攻击情况报告
- 统计当日和前一日的攻击事件数量
- 计算攻击事件的增减比例
- 统计高危攻击事件数量及占比
##### 4.2.2 内网高危行为报告
- 统计当日和前一日的高危事件数量
- 计算高危事件的增减比例
##### 4.2.3 用户问题报告
- 统计22:00后未关机的电脑数量
- 计算未关机电脑的比例，包括产线和非产线电脑
### 4.3 生成报告内容

### 4.4 发送邮件


# 备注
## 1. 重新考虑数据的流向问题。现在我有task，如何将现有的task和celery的task相连接？这个是要思考的问题
第一步，先考虑现在task的结构
## 2. 第二，如果能连接成功，那么就已经有频率问题，现在的频率是自己定义的，用的是string，如何绑定celery的频率呢？
## 3. 我已经有定义好的任务了，并且任务也可以定时执行了，那么现在就要考虑在任务中添加一些功能，比如在数据库中写入一下数据比如说
  1. task执行完毕要有执行日志吧，现在已经提供给你一个日志，我可能需要改一下这个日志的界面，这个优先级比较低，暂时不考虑
  2. task的执行结果，是需要发邮件的，邮件的内容是需要根据模版来的，流程是这样的 读取数据 -> 提取数据并计算对应的参数 -> 根据读取的数据填入对应的模板-> 将补充完毕的模板按照邮件列表 挨个发送-> 记录邮件发送的日志，不管是发送成功还是失败
  3. 等下，我需要先理一下简报，模板，任务之间关系。首先任务是决定定时执行的，定时获取数据这个没问题。当发送的时候，会根据简报来发送吗？比如我有一个安全攻击的简报，定时到了，读取对应的数据，根据简报类型，简报分组，简报模板，结合参数发送数据，同时记录一下发送记录。**而定时任务执行日志，如何设置暂时不考虑**。重点在与简报类型，比如说日报，那就是发送频率一日一次，如果是安全漏洞，则可能是安全漏洞类型的模板。话说模板和分组的区别是什么？同一个分组会使用不同的模板吗？除非是三者共同决定一个简报的内容。用户使用的时候，可能会在模板管理界面新增一个模板，这个时候就会指定模板的类型和模板分组以及模板内容。而新建简报的时候就是要发送给邮件的内容，是用上面这些东西生成后的了。生成一次就会产生一次邮件发送记录。**当用户删除这个简报的时候，对应的定时任务如何处理？** 当用户删除的时候，这个简报肯定就不存在了。所以要删除对应表里面的数据。现在如果用户新建了一个模板，用到了，指定了这些数据应该应该这么去。然后，用户会在定时任务中新建一个定时任务，可能会用到这个模板，然后呢当定时任务启动的时候，就会用这个模板产生对应的简报，简报对应的信息会在简报列表中出现。当用户删除这个简报的时候，对应的定时任务也应该停止。一个定时任务只可能对应唯一的简报。那么对应到代码中，就产生了几个问题
  1. 定时任务是可变的，因为简报是可以重新生成的，比如换一个模板，换一个定时频率就会产生新的简报，因此就没有办法在代码中写死定时任务，在celery的管理界面，只能指定写死在代码中的task，设置这个task的执行频率，是否启动，是否停止？并且用户是可以直接在前端界面直接生成新的定时任务的。这个问题如何解决？


完善Report和Template模型
设计Task模型来关联Report、Template和定时任务
实现generate_and_send_report任务函数的具体逻辑
设计用户界面和API来创建、管理定时任务
处理任务的执行日志和邮件发送记录
 
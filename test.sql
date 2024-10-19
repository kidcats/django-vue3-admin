-- ReportType 数据 t6NCtd6GJiRsCCGZ
INSERT INTO dvadmin_report_types (name, description, create_datetime, update_datetime) VALUES
('日报', '每日简报', NOW(), NOW()),
('周报', '每周简报', NOW(), NOW()),
('月报', '每月简报', NOW(), NOW()),
('季报', '每季简报', NOW(), NOW()),
('年报', '每年简报', NOW(), NOW()),
('其他简报', '其他简报', NOW(), NOW());

-- ReportGroup 数据
INSERT INTO dvadmin_report_groups (name, description, create_datetime, update_datetime) VALUES
('安全漏洞', '安全相关简报', NOW(), NOW()),
('钓鱼邮件', '钓鱼邮件', NOW(), NOW());

-- Frequency 数据
INSERT INTO dvadmin_report_frequencies (name, cron_expression, description, is_active, create_datetime, update_datetime) VALUES
('每天8点', '0 8 * * *', '每天早上8点执行', TRUE, NOW(), NOW()),
('每周一10点', '0 10 * * 1', '每周一上午10点执行', TRUE, NOW(), NOW()),
('每月1号12点', '0 12 1 * *', '每月1号中午12点执行', TRUE, NOW(), NOW());

-- Users 数据（假设已存在，这里使用示例ID）
-- INSERT INTO dvadmin_system_users (username, password, email) VALUES
-- ('admin', 'hashed_password', 'admin@example.com');

-- Report 数据
INSERT INTO dvadmin_report_reports (title, type_id, summary, content, report_date, report_group_id, creator_id, create_datetime, update_datetime) VALUES
('日常安全简报', 1, '今日安全概况', '详细内容...', CURRENT_DATE, 1, 1, NOW(), NOW()),
('周度运维报告', 2, '本周运维总结', '详细内容...', CURRENT_DATE, 2, 1, NOW(), NOW()),
('月度管理层简报', 3, '本月管理概要', '详细内容...', CURRENT_DATE, 2, 1, NOW(), NOW());

-- EmailSendRecord 数据
INSERT INTO dvadmin_report_email_send_records (report_id, sent_at, recipients, status, create_datetime, update_datetime) VALUES
(1, NOW(), 'user1@example.com;user2@example.com', '成功', NOW(), NOW()),
(2, NOW(), 'user3@example.com;user4@example.com', '成功', NOW(), NOW()),
(3, NOW(), 'manager@example.com', '成功', NOW(), NOW());

-- Template 数据
INSERT INTO dvadmin_report_templates (template_type_id, template_group_id, template_name, content, creator_id, create_datetime, update_datetime) VALUES
(1, 1, '日报模板', '日报模板内容...', 1, NOW(), NOW()),
(2, 2, '周报模板', '周报模板内容...', 1, NOW(), NOW()),
(3, 2, '月报模板', '月报模板内容...', 1, NOW(), NOW());

-- ScheduledTask 数据
INSERT INTO dvadmin_report_scheduled_tasks (name, frequency_id, template_id, status, creator_id, create_datetime, update_datetime) VALUES
('每日安全报告任务', 1, 1, '运行中', 1, NOW(), NOW()),
('每周运维报告任务', 2, 2, '运行中', 1, NOW(), NOW()),
('每月管理报告任务', 3, 3, '运行中', 1, NOW(), NOW());

-- TaskLog 数据
INSERT INTO dvadmin_report_task_logs (job_id, task_name, start_time, end_time, result, parameters, error_info, create_datetime, update_datetime) VALUES
('job1', '每日安全报告任务', NOW() - INTERVAL '1 hour', NOW(), '成功', '{}', '无', NOW(), NOW()),
('job2', '每周运维报告任务', NOW() - INTERVAL '2 hour', NOW() - INTERVAL '1 hour', '成功', '{}', '无', NOW(), NOW()),
('job3', '每月管理报告任务', NOW() - INTERVAL '3 hour', NOW() - INTERVAL '2 hour', '成功', '{}', '无', NOW(), NOW());

-- IntermediateData 数据
INSERT INTO dvadmin_report_intermediate_datas 
(date, internal_attacks, external_attacks, other_metrics, job_id, create_datetime, update_datetime) 
VALUES
(CURRENT_DATE, 10, 20, '{"metric1": 5, "metric2": 15}', 1, NOW(), NOW()),
(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), 15, 25, '{"metric1": 8, "metric2": 18}', 1, NOW(), NOW()),
(DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), 12, 22, '{"metric1": 6, "metric2": 16}', 1, NOW(), NOW());

-- EmailConfiguration 数据
INSERT INTO dvadmin_report_email_configurations (report_type_id, recipients, status, creator_id, create_datetime, update_datetime) VALUES
(1, 'security@example.com;manager@example.com', TRUE, 1, NOW(), NOW()),
(2, 'ops@example.com;manager@example.com', TRUE, 1, NOW(), NOW()),
(3, 'ceo@example.com;cfo@example.com', TRUE, 1, NOW(), NOW());
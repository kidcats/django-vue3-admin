// crudOptions.ts
import { 
    compute,
    CreateCrudOptionsProps, 
    CreateCrudOptionsRet, 
    dict, 
    EditReq,
    Dict
} from "@fast-crud/fast-crud";
import { ElMessage } from 'element-plus';
import cronstrue from 'cronstrue';
import 'cronstrue/locales/zh_CN';
import { 
    create, 
    getList,
    pause, 
    remove, 
    resume, 
    update 
} from "./api";
import { getList as getTemplateList, Template } from "../templateViewSet/api";
import { TemplateRow } from "../templateViewSet/crud";
import { FrequencyRow, getReportTypeList, ReportGroupRow } from "../api";

export type ScheduledTaskRow = {
    id?: number;
    name?: string;
    frequency?: FrequencyRow;
    template?: TemplateRow;
    status?: string;
    create_datetime?: string;
    update_datetime?: string;
    report_template?: ReportGroupRow;
} & Record<string, any>;

function generateCronDescription(cronExpression: string): string {
    try {
        return cronstrue.toString(cronExpression, { locale: "zh_CN" });
    } catch (error) {
        console.error('解析 Cron 表达式时出错:', error);
        return '无效的 Cron 表达式';
    }
}

export default function ({ crudExpose, context }: CreateCrudOptionsProps<ScheduledTaskRow>): CreateCrudOptionsRet<ScheduledTaskRow> {
    
    const editRequest = ({ form, row }: { form: any, row: ScheduledTaskRow }) => {
        const id = Number(row.id);
        if (isNaN(id)) {
          throw new Error('Invalid id for update operation');
        }
        const { id: _, ...updateData } = form;
        return update(id, updateData);
    }
    
    return {
        crudOptions: {
            request: {
                pageRequest: getList,
                addRequest: create,
                editRequest,
                delRequest: remove,
            },
            columns: {
                name: {
                    title: "任务名称",
                    type: "text",
                    search: { show: true },
                },
                'frequency.cron_expression': {
                    title: "执行频率",
                    type: "component",
                    column: {
                        formatter: (data: any) => {
                            return (data.row.frequency?.description || '');
                        }
                    },
                    form: {
                        rules: [
                            { required: true, message: 'Cron 表达式必填', trigger: 'blur' },
                            {
                                validator: (_: any, value: string, callback: any) => {
                                    const parts = value.trim().split(/\s+/);
                                    if (parts.length !== 5) {
                                        callback(new Error('Cron 表达式格式不正确'));
                                    } else {
                                        callback();
                                    }
                                },
                                trigger: 'blur'
                            }
                        ],
                        helper: {
                            render({ form }) {
                                const cronExpr = form?.frequency?.cron_expression || '';
                                const description = generateCronDescription(cronExpr);
                                return (
                                    <div>
                                        <p>Cron 表达式描述: {description}</p>
                                    </div>
                                );
                            }
                        },
                    },
                    valueBuilder({ form, row }: { form: any, row: ScheduledTaskRow }) {
                        form.frequency = form.frequency || {};
                        form.frequency.cron_expression = row.frequency?.cron_expression || '* * * * *';
                    },
                    valueResolve({ form, row }: { form: any, row: ScheduledTaskRow }) {
                        if(row.frequency){
                        row.frequency = row.frequency || {};
                        row.frequency.cron_expression = form.frequency.cron_expression;}
                    },
                },
                create_datetime: {
                    title: "创建时间",
                    type: "datetime",
                    column: { show: true },
                    form: { show: false },
                },
                update_datetime: {
                    title: "更新时间",
                    type: "datetime",
                    column: { show: true },
                    form: { show: false },
                },
                status: {
                    title: "状态",
                    type: "dict-text",
                    form: { show: false },
                },
                template: {
                    title: "模板分组",
                    type: "dict-select",
                    dict: dict({
                        getData: getTemplateList,
                    }),
                    column: {
                        formatter: (data: any) => {
                            return (data.row.template?.template_name || '');
                        }
                    },
                    form: {
                        rules: [{ required: true, message: '请选择模板分组', trigger: 'change' }],
                    },
                },
            },
            search: {
                show: true,
                buttons: {
                    reset: { show: false },
                    search: { type: 'primary' },
                },
            },
            actionbar: {
                show: false,
            },
            toolbar: {
                show: false,
            },
            rowHandle: {
                width: 240,
                buttons: {
                    view: { show: false },
                    edit: { 
                        text: '编辑',
                    },
                    remove: { text: '删除' },
                    pause: {
                        text: '停止',
                        click: ({ row }: { row: ScheduledTaskRow }) => {
                            if (typeof row.id === 'number') {
                                pause(row.id).then(() => {
                                    ElMessage.success('任务已停止');
                                    crudExpose.doRefresh();
                                }).catch(err => {
                                    ElMessage.error('停止任务失败: ' + err.message);
                                });
                            } else {
                                ElMessage.error('无效的任务ID');
                            }
                        },
                    },
                    resume: {
                        text: '运行',
                        click: ({ row }: { row: ScheduledTaskRow }) => {
                            if (typeof row.id === 'number') {
                                resume(row.id).then(() => {
                                    ElMessage.success('任务已启动');
                                    crudExpose.doRefresh();
                                }).catch(err => {
                                    ElMessage.error('启动任务失败: ' + err.message);
                                });
                            } else {
                                ElMessage.error('无效的任务ID');
                            }
                        },
                    },
                },
            },
            pagination: {
                pageSize: 20,
                pagerCount: 5,
            },
        },
    };
}
import { CreateCrudOptionsProps, CreateCrudOptionsRet, FsButton, dict } from "@fast-crud/fast-crud";
import { ElMessage } from 'element-plus';
import { getList } from "./api";

export type TaskLog = {
    id?: number;
    job_id: string;
    task_name: string;
    start_time: string;
    end_time: string | null;
    result: '成功' | '失败' | '执行中';
};

export default function ({ crudExpose }: CreateCrudOptionsProps<TaskLog>): CreateCrudOptionsRet<TaskLog> {
    return {
        crudOptions: {
            request: {
                pageRequest: getList,
            },
            search: {
                show: true,
                options: {
                    labelWidth: '80px',
                },
                buttons: {
                    search: {
                        ...FsButton,
                        text: '查询',
                        type: 'primary',
                    },
                    reset: { show: false },
                },
            },
            actionbar: {
                show: false,
            },
            toolbar: {
                show: false,
            },
            table: {
                border: true,
                highlightCurrentRow: true,
            },
            columns: {
                job_id: {
                    title: "job_id",
                    type: "text",
                    column: {
                        width: 100,
                    },
                },
                task_name: {
                    title: "任务名称",
                    type: "text",
                    search: { show: true },
                    column: {
                        width: 200,
                    },
                },
                start_time: {
                    title: "开始时间",
                    type: "datetime",
                    column: {
                        width: 180,
                    },
                },
                end_time: {
                    title: "结束时间",
                    type: "datetime",
                    column: {
                        width: 180,
                    },
                },
                result: {
                    title: "执行结果",
                    type: "dict-select",
                    dict: dict({
                        data: [
                            { value: '成功', label: '成功' },
                            { value: '失败', label: '失败' },
                            { value: '执行中', label: '执行中' },
                        ],
                    }),
                    column: {
                        width: 100,
                    },
                },
            },
            rowHandle: {
                width: 180,
                buttons: {
                    view: {
                        text: '详情',
                        type: 'text',
                        click: ({ row }) => {
                            console.log('查看详情', row);
                            // 实现查看详情的逻辑
                        },
                    },
                    rerun: {
                        text: '再次执行',
                        type: 'text',
                        show: ({ row }) => row.result !== '执行中',
                        click: async ({ row }) => {
                            try {
                                await rerun(row.job_id);
                                ElMessage.success('任务已重新执行');
                                await crudExpose.doRefresh();
                            } catch (error) {
                                ElMessage.error('重新执行失败');
                            }
                        },
                    },
                    stop: {
                        text: '停止',
                        type: 'text',
                        show: ({ row }) => row.result === '执行中',
                        click: async ({ row }) => {
                            try {
                                await stop(row.job_id);
                                ElMessage.success('任务已停止');
                                await crudExpose.doRefresh();
                            } catch (error) {
                                ElMessage.error('停止任务失败');
                            }
                        },
                    },
                },
            },
            pagination: {
                pageSize: 20,
                pagerCount: 7,
                layout: 'total, sizes, prev, pager, next, jumper',
                pageSizes: [10, 20, 50, 100],
            },
        },
    };
}
import { CreateCrudOptionsProps, CreateCrudOptionsRet, FsButton, dict, utils } from "@fast-crud/fast-crud";
import { getList, create, update } from "./api";
import { ElMessage } from 'element-plus';
import { ref } from "vue";

export type IntermediateTableRow = {
    id?: number;
    out_count: number;
    out_high: number;
    out_time_range: string;
    in_count: number;
    in_high: number;
    in_time_range: string;
    electric_count: number;
    unfinished_count: number;
    production_unfinished_count: number;
    quality_unfinished_count: number;
    unfinished_time_range: string;
    date: string;
    type: string;
    job_id: string;
};

export default function ({ crudExpose, context }: CreateCrudOptionsProps<IntermediateTableRow>): CreateCrudOptionsRet<IntermediateTableRow> {
    const selectedRowKeys = ref([]);
    context.selectedRowKeys = selectedRowKeys;

    return {
        crudOptions: {
            request: {
                pageRequest: getList,
                addRequest: create,
                editRequest: update,
            },
            columns: {
                out_count: { 
                    title: "外网攻击", 
                    type: "number",
                    form: {
                        component: { name: 'el-input-number' }
                    }
                },
                out_high: { 
                    title: "外网高危", 
                    type: "number",
                    form: {
                        component: { name: 'el-input-number' }
                    }
                },
                out_time_range: { 
                    title: "外网攻击重复时间段", 
                    type: "text" 
                },
                in_count: { 
                    title: "内网攻击", 
                    type: "number",
                    form: {
                        component: { name: 'el-input-number' }
                    }
                },
                in_high: { 
                    title: "内网高危", 
                    type: "number",
                    form: {
                        component: { name: 'el-input-number' }
                    }
                },
                in_time_range: { 
                    title: "内网攻击重复时间段", 
                    type: "text" 
                },
                electric_count: { 
                    title: "电磁泄露", 
                    type: "number",
                    form: {
                        component: { name: 'el-input-number' }
                    }
                },
                unfinished_count: { 
                    title: "未关机器", 
                    type: "number",
                    form: {
                        component: { name: 'el-input-number' }
                    }
                },
                production_unfinished_count: { 
                    title: "产线未关机器", 
                    type: "number",
                    form: {
                        component: { name: 'el-input-number' }
                    }
                },
                quality_unfinished_count: { 
                    title: "质量未关机器", 
                    type: "number",
                    form: {
                        component: { name: 'el-input-number' }
                    }
                },
                unfinished_time_range: { 
                    title: "未关机器时间段", 
                    type: "text" 
                },
                date: { 
                    title: "日期", 
                    type: "date",
                    form: {
                        component: { name: 'el-date-picker' }
                    }
                },
                type: { title: "类型", type: "text" },
                job_id: { title: "job_id", type: "text" },
            },
            search: {
                show: true,
                options: {
                    labelWidth: '80px',
                },
                columns: {
                    date: {
                        title: "日期",
                        component: {
                            name: 'el-date-picker',
                            props: {
                                type: 'daterange',
                                rangeSeparator: '~',
                                startPlaceholder: '开始日期',
                                endPlaceholder: '结束日期'
                            }
                        }
                    }
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
                buttons: {
                    add: { 
                        show: true,
                        text: '新增'
                    },
                },
            },
            toolbar: {
                show: false,
            },
            table: {
                border: true,
                stripe: true,
                highlightCurrentRow: true,
            },
            rowHandle: {
                width: 100,
                buttons: {
                    edit: {
                        text: '修改',
                        type: 'text',
                    },
                },
            },
            form: {
                wrapper: {
                    is: 'el-dialog',
                    props: {
                        title: '编辑中间表数据',
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
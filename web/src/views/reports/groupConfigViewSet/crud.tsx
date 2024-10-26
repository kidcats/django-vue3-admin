// crud.ts
import { CreateCrudOptionsProps, CreateCrudOptionsRet, FsButton, dict, utils } from "@fast-crud/fast-crud";
import { getReportCategories, createReportCategory, updateReportCategory, deleteReportCategory } from "./api";
import { ref } from "vue";

// 定义行数据类型
export type ReportCategoryRow = {
    id?: number;
    name: string;
    description: string;
    category_type: number;
    created_at: string;
    updated_at: string;
    creator: string;
};

export default function ({ crudExpose, context }: CreateCrudOptionsProps<ReportCategoryRow>): CreateCrudOptionsRet<ReportCategoryRow> {
    const selectedRowKeys = ref([]);
    context.selectedRowKeys = selectedRowKeys;

    return {
        crudOptions: {
            request: {
                pageRequest: getReportCategories,
                addRequest: createReportCategory,
                editRequest: updateReportCategory,
                delRequest: ({ row }) => deleteReportCategory(row.id, row.category_type)
            },
            columns: {
                id: {
                    title: 'ID',
                    type: 'number',
                    column: {
                        width: 50
                    },
                    form: {
                        show: false
                    }
                },
                category_type: {
                    title: '分类类型',
                    type: 'dict-select',
                    dict: dict({
                        data: [
                            { value: 0, label: '模板类型' },
                            { value: 1, label: '模板分组' }
                        ]
                    }),
                    form: {
                        rules: [{ required: true, message: '请选择分类类型' }],
                    }
                },
                name: {
                    title: '名称',
                    type: 'text',
                    search: {
                        show: true
                    },
                    form: {
                        rules: [
                            { required: true, message: '请输入名称' }
                        ]
                    }
                },
                description: {
                    title: '描述',
                    type: 'text',
                    column: {
                        width: 300,
                        showOverflowTooltip: true
                    }
                },
                created_at: {
                    title: '创建时间',
                    type: 'datetime',
                    column: {
                        width: 180
                    },
                    form: {
                        show: false
                    }
                },
                updated_at: {
                    title: '更新时间',
                    type: 'datetime',
                    column: {
                        width: 180
                    },
                    form: {
                        show: false
                    }
                },
                creator: {
                    title: '创建人',
                    type: 'text',
                    form: {
                        show: false
                    }
                }
            },
            search: {
                show: true,
                options: {
                    labelWidth: '80px',
                },
                columns: {
                    name: {
                        title: '名称',
                        component: {
                            name: 'el-input',
                            props: {
                                placeholder: '请输入名称搜索'
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
                    reset: { show: true },
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
                width: 160,
                buttons: {
                    edit: {
                        text: '修改',
                        type: 'text',
                    },
                    delete: {
                        text: '删除',
                        type: 'text',
                        props: { type: 'danger' }
                    }
                },
            },
            form: {
                wrapper: {
                    is: 'el-dialog',
                    props: {
                        title: '编辑分类',
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
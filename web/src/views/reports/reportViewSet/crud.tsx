import { CreateCrudOptionsProps, CreateCrudOptionsRet, FsButton, dict } from "@fast-crud/fast-crud";
import { getList, create, update, remove, getReportTypes, getEmailHistory, getReportGroups } from "./api";
import { ElMessage, ElMessageBox } from 'element-plus';
import { ref } from "vue";
import { getReportGroup, ReportGroupRow, ReportTypeRow } from "../api";

// 这个很重要，因为pagerequest返回的列表就要跟这个对其
// 同时下面column里面的行字段匹配的时候也会根据这个类里面的字段名匹配上

export type ReportRow = {
    id?: number;
    title?: string;
    type?: ReportTypeRow;
    summary?: string;
    create_datetime?: string;
    group?: ReportGroupRow;
};

const emailHistory = ref([]);

export default function ({ crudExpose, context }: CreateCrudOptionsProps<ReportRow>): CreateCrudOptionsRet<ReportRow> {
    const selectedRowKeys = ref([]);
    context.selectedRowKeys = selectedRowKeys;
    const showEmailHistory = async (row: ReportRow) => {
        if (row.id === undefined) {
            ElMessage.error('记录 ID 不存在，无法获取邮件历史');
            return;
        }
        try {
            const response = await getEmailHistory(row.id);
            emailHistory.value = response.data;
    
            const tableHTML = `
                <style>
                    .custom-message-box .el-message-box__header {
                        display: none;
                    }
                    .custom-message-box .el-message-box__btns {
                        text-align: center;
                    }
                    .custom-message-box .el-message-box__container {
                        display: flex;
                        justify-content: center;
                        width: 100%;
                    }
                    .custom-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-family: Helvetica Neue,Helvetica,PingFang SC,Hiragino Sans GB,Microsoft YaHei,SimSun,sans-serif;
                        font-size: 14px;
                        table-layout: auto;
                    }
                    .custom-table th, .custom-table td {
                        border: 1px solid #EBEEF5;
                        padding: 12px;
                        text-align: left;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        max-width: 200px;
                    }
                    .custom-table th {
                        background-color: #F5F7FA;
                        color: #909399;
                        font-weight: 500;
                    }
                    .custom-table tr:nth-child(even) {
                        background-color: #FAFAFA;
                    }
                    .custom-table tr:hover {
                        background-color: #F5F7FA;
                    }
                    .custom-message-box .el-message-box__content {
                        overflow-y: auto;
                    }
                    .custom-message-box .el-message-box__message {
                        margin-top: 0;
                        width:100%;
                    }
                    .custom-message-box {
                        width: 90vw;
                        max-width: 1200px;
                    }
                    .table-wrapper {
                        overflow-x: auto;
                        max-width: 100%;
                    }
                </style>
                <div class="table-wrapper">
                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th>描述</th>
                                <th>发送时间</th>
                                <th>更新时间</th>
                                <th>创建时间</th>
                                <th>创建者</th>
                                <th>收件人</th>
                                <th>状态</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${emailHistory.value.map(item => `
                                <tr>
                                    <td title="${item.description || '-'}">${item.description || '-'}</td>
                                    <td title="${item.sent_at || '-'}">${item.sent_at || '-'}</td>
                                    <td title="${item.update_datetime || '-'}">${item.update_datetime || '-'}</td>
                                    <td title="${item.create_datetime || '-'}">${item.create_datetime || '-'}</td>
                                    <td title="${item.creator_name || '-'}">${item.creator_name || '-'}</td>
                                    <td title="${item.recipients || '-'}">${item.recipients || '-'}</td>
                                    <td title="${item.status || '-'}">${item.status || '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
    
            ElMessageBox({
                title: '邮件历史',
                message: tableHTML,
                dangerouslyUseHTMLString: true,
                showCancelButton: true,
                cancelButtonText: '关闭',
                customClass: 'custom-message-box',
                beforeClose: (action, instance, done) => {
                    done();
                }
            }).catch(() => {
                // 处理取消操作
            });
        } catch (error) {
            console.error(error);
            ElMessage.error('获取邮件历史失败');
        }
    };
    return {
        crudOptions: {
            settings: {
                plugins: {
                    //这里使用行选择插件，生成行选择crudOptions配置，最终会与crudOptions合并
                    rowSelection: {
                        enabled: true,
                        order: -2,
                        before: true,
                        // handle: (pluginProps,useCrudProps)=>CrudOptions,
                        props: {
                            multiple: true,
                            crossPage: true,
                            selectedRowKeys,
                            onSelectedChanged(selected) {
                                console.log("已选择变化：", selected);
                            }
                        }
                    }
                }
            },
            request: {
                pageRequest: getList,
                addRequest: create,
                editRequest: update,
                delRequest: remove,
                searchRequest: getList,
            },
            columns: {
                type: {
                    title: "类型",
                    type: "dict-radio",
                    dict: dict({
                        getData: async () => {
                            const response = await getReportTypes();
                            return response.data.map((item: any) => ({
                                value: item.id,
                                label: item.name,
                            }));
                        },
                    }),
                    column: {
                        formatter: (data: any) => {
                            return data.row.type?.name || '-';  // 使用可选链访问 name，如果不存在则返回 '-'
                        }
                    },
                    form: {
                        rules: [{ required: true, message: '请选择类型', trigger: 'change' }],
                    },
                    search: { show: true },
                },
                group: {
                    title: "分组",
                    type: "dict-radio",
                    dict: dict({
                        getData: async () => {
                            const response = await getReportGroups();
                            return response.data.map((item: any) => ({
                                value: item.id,
                                label: item.name,
                            }));
                        },
                    }),
                    column: {
                        formatter: (data: any) => {
                            return data.row.type?.name || '-';  // 使用可选链访问 name，如果不存在则返回 '-'
                        }
                    },
                    form: {
                        rules: [{ required: true, message: '请选择类型', trigger: 'change' }],
                    },
                    search: { show: true },
                },
                title: {
                    title: "标题",
                    type: "text",
                    column: {
                        resizable: true,
                        // sorter: true, // 如果需要排序
                    },
                    form: {
                        rules: [{ required: true, message: '请输入标题', trigger: 'blur' }],
                    },
                    search: { show: true },
                },
                summary: {
                    title: "摘要",
                    type: "textarea",
                    column: {
                        resizable: true,
                    },
                    form: {
                        rules: [{ required: true, message: '请输入摘要', trigger: 'blur' }],
                    },
                },
                create_datetime: {
                    title: "日期时间",
                    type: "datetime",
                    search: {
                        show: true,
                        title: "筛选时间",
                        col: {
                            span: 6
                        },
                        //查询显示范围选择
                        component: {
                            type: "datetimerange"
                        }
                    },
                    form: {
                        component: {
                            //输入输出值格式化
                            valueFormat: "YYYY-MM-DD HH:mm:ss"
                        }
                    }
                },
            },
            search: {
                show: true,
                options: {
                    labelWidth: '100px',
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
                buttons: {
                    add: { show: true }, // 显示新增按钮
                    custom: {
                        text: '简报列表',
                        type: 'primary',
                        // icon: 'el-icon-document',
                        validate: false, // 根据需求决定是否需要选中行
                        click: () => {
                            // 跳转到简报列表页面
                            context.router.push({ name: 'ReportList' });
                        },
                    },
                },
            },
            toolbar: {
                show: true,
                buttons: {
                    search: { show: false },
                    refresh: { show: false },
                    compact: { show: false },
                    export: { show: false },
                    columns: { show: false },
                    custom: {
                        text: '批量删除',
                        type: 'danger',
                        // icon: 'el-icon-delete',
                        validate: true, // 需要选中行才能启用按钮
                        click: async () => {
                            // 使用类型断言访问内部的 tableStore
                            const crudBindingValue = crudExpose.crudBinding.value as any;
                            const selected = crudBindingValue.tableStore.getSelectionRows();

                            if (!selected || selected.length === 0) {
                                ElMessage.warning('请至少选择一条记录');
                                return;
                            }

                            // 过滤掉可能为 undefined 的 ID
                            const ids = selected.map((row: ReportRow) => row.id).filter((id: number | undefined): id is number => id !== undefined);

                            if (ids.length === 0) {
                                ElMessage.warning('所选记录没有有效的 ID，无法删除');
                                return;
                            }

                            try {
                                await remove(ids);
                                ElMessage.success('批量删除成功');
                                await crudExpose.doRefresh(); // 使用 doRefresh 方法刷新数据
                            } catch (error) {
                                console.error(error);
                                ElMessage.error('批量删除失败');
                            }
                        },
                    },
                },
            },
            table: {
                border: true,
                selection: true,
                highlightCurrentRow: true,
                // 更多表格配置
            },
            rowHandle: {
                width: 180,
                buttons: {
                    view: {
                        show: false,
                        text: '查看',
                        type: 'text',
                        click: ({ row }) => {
                            if (row.id !== undefined) {
                                context.router.push({ name: 'ReportView', params: { id: row.id } });
                            } else {
                                ElMessage.error('记录 ID 不存在');
                            }
                        },
                    },
                    edit: {
                        show: true,
                        text: '邮件历史',
                        type: 'info',
                        click: ({ row }: { row: ReportRow }) => {
                            showEmailHistory(row);
                        },
                    },
                    remove: {
                        show: true,
                        text: '删除',
                        type: 'danger',
                        click: async ({ row }) => {
                            if (row.id === undefined) {
                                ElMessage.error('记录 ID 不存在，无法删除');
                                return;
                            }
                            try {
                                await remove(row.id);
                                ElMessage.success('删除成功');
                                await crudExpose.doRefresh(); // 使用 doRefresh 方法刷新数据
                            } catch (error) {
                                console.error(error);
                                ElMessage.error('删除失败');
                            }
                        },
                    },
                },
            },
            form: {
                wrapper: {
                    is: 'el-dialog',
                    props: {
                        title: '编辑报表',
                        fullscreen: false,
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
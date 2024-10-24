import { CreateCrudOptionsProps, CreateCrudOptionsRet, FsButton, dict, compute } from "@fast-crud/fast-crud";
import { getList, create, update, remove, updateStatus, getReportTypes } from "./api";
import { ElMessage } from 'element-plus';
import { ref } from "vue";
import { ReportTypeRow } from "../api";

export type EmailConfigRow = {
    id?: number;
    report_type?: ReportTypeRow | string | number;
    recipients?: string;
    status?: boolean;
    creator_id?: number;
    create_datatime?: string;
    update_datatime?: string;
}& Record<string, any>;

export default function ({ crudExpose, context }: CreateCrudOptionsProps<EmailConfigRow>): CreateCrudOptionsRet<EmailConfigRow> {
    const selectedRowKeys = ref([]);
    context.selectedRowKeys = selectedRowKeys;
    const editRequest = ({ form, row }: { form: any, row: EmailConfigRow }) => {
        if (form.id == null) {
            form.id = row.id;
        }
        const { id, ...updateData } = form;
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
                'report_type.name': {
                    title: "模板分组",
                    type: "dict-select",
                    dict: dict({
                        url: 'api/report-type',
                        value: 'id',
                        label: 'name',
                        onReady: (dictsData) => {
                          console.log('report Dict:', dictsData);
                        }
                      }),
                    form: {
                        key: ["report_type", "name"],
                    }
                },
                recipients: {
                    title: "邮件接收人",
                    type: "text",
                    column: {
                        width: 300,
                        showOverflowTooltip: true,
                    },
                    form: {
                        component: {
                            placeholder: '多个邮箱用分号分隔',
                        },
                        rules: [{ required: true, message: '请输入邮件接收人', trigger: 'blur' }],
                    },
                },
                status: {
                    title: "状态",
                    type: "dict-switch",
                    form: {
                        component: {
                          onChange: compute((context) => {
                            //动态onChange方法测试
                            return () => {
                              console.log("onChange", context.form.switch);
                            };
                          })
                        }
                      },
                    dict: dict({
                        data: [
                            { value: true, label: '启用' },
                            { value: false, label: '禁用' },
                        ],
                    }),
                    column: {
                        width:180,
                        component: {
                            name: 'fs-dict-switch',
                            events: {
                                onChange: async ({ row }) => {
                                    try {
                                        await updateStatus(row.id!, row.status!);
                                        ElMessage.success('状态更新成功');
                                    } catch (error) {
                                        console.error(error);
                                        ElMessage.error('状态更新失败');
                                        row.status = !row.status;  // 恢复原状态
                                    }
                                },
                            },
                        },
                    },
                },
                create_datatime: {
                    title: "创建时间",
                    type: "datetime",
                    column: {
                        width: 250,
                    },
                    form: {
                        show: false,
                    },
                },
            },
            toolbar:{
                show:false,
            },
            actionbar: {
                buttons: {
                    add: { show: true },
                },
            },
            rowHandle: {
                buttons: {
                    view:{show:false},
                    edit: { show: true },
                    remove: { text: '删除',
                        click: ({ row }: { row: EmailConfigRow }) => {
                            if (typeof row.id === 'number') {
                                remove(row.id).then(() => {
                                    ElMessage.success('任务已删除');
                                    crudExpose.doRefresh();
                                }).catch(err => {
                                    ElMessage.error('删除任务失败: ' + err.message);
                                });
                            } else {
                                ElMessage.error('无效的任务ID');
                            }
                        },
                     },
                },
            },
            search: {
                show: false,
            },
            form: {
                wrapper: {
                    is: 'el-dialog',
                    props: {
                        title: '邮件配置',
                        width: '50%',
                    },
                },
                beforeSubmit: ({ form }) => {
                    console.log('BeforeSubmit - form:', form);
                    if (form.report_type) {
                      // 确保只发送 id
                      console.log(form.report_type);
                      if(typeof form.report_type === "object"){
                        if(typeof form.report_type.name === "string"){
                            form.report_type = form.report_type.id;
                        }else{
                            form.report_type = form.report_type.name;
                        }
                      }
                      else{
                        form.report_type = form.report_type;
                      }
                    }
                    return form;
                  }
            },
            table: {
                border: true,
                stripe: true,
                highlightCurrentRow: true,
            },
            pagination: {
                pageSize: 20,
                pageSizes: [10, 20, 50, 100],
            },
        },
    };
}
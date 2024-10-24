import { CreateCrudOptionsProps, CreateCrudOptionsRet, FsButton, compute, dict, utils } from "@fast-crud/fast-crud";
import { getList, create, update, remove, getTemplateTypes, getTemplateGroups } from "./api";
import { ElMessage } from 'element-plus';
import { ref } from "vue";
import { ReportGroupRow, ReportTypeRow } from "../api";
import { FsUploaderFormOptions } from "@fast-crud/fast-extends";

export type TemplateRow = {
    id?: number;
    template_type?: ReportTypeRow | number;
    template_group?: ReportGroupRow | number;
    template_name?: string;
    content?: string;
    creator_name?: string;
    create_datetime?: string;
} & Record<string, any>;

export default function ({ crudExpose, context }: CreateCrudOptionsProps<TemplateRow>): CreateCrudOptionsRet<TemplateRow> {
    const selectedRowKeys = ref([]);
    context.selectedRowKeys = selectedRowKeys;
    const editRequest = ({ form, row }: { form: any, row: TemplateRow }) => {
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
                'template_type.name': {
                    title: "模板类型",
                    type: "dict-select",
                    dict: dict({
                        url: 'api/report-type',
                        value: 'id',
                        label: 'name',
                        onReady: (dictsData) => {
                          console.log('Template Dict:', dictsData);
                        }
                      }),
                    form: {
                        key: ["template_type", "name"],
                    }
                },
                'template_group.name': {
                    title: "模板分组",
                    type: "dict-select",
                    dict: dict({
                        url: 'api/report-group',
                        value: 'id',
                        label: 'name',
                        onReady: (dictsData) => {
                          console.log('Template Dict:', dictsData);
                        }
                      }),
                    form: {
                        key: ["template_group", "name"],
                    }
                },
                template_name: {
                    title: "模板名称",
                    type: "text",
                    column: {
                        resizable: true,
                    },
                    form: {
                        rules: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
                    },
                    search: { show: true },
                },
                content: {
                    title: "内容",
                    column: {
                        width: 300,
                        show: false
                    },
                    type: "editor-wang5", // 富文本图片上传依赖file-uploader，请先配置好file-uploader
                    form: {
                        col: { span: 24 },

                        rules: [
                            { required: true, message: "此项必填" },
                            {
                                validator: async (rule, value) => {
                                    if (value.trim() === "<p><br></p>") {
                                        throw new Error("内容不能为空");
                                    }
                                }
                            }
                        ],
                        component: {
                            disabled: compute(({ form }) => {
                                return form.disabled;
                            }),
                            id: "1", // 当同一个页面有多个editor时，需要配置不同的id
                            toolbarConfig: {},
                            editorConfig: {},
                            onOnChange(value: any) {
                                console.log("value changed", value);
                            },
                            uploader: {
                                type: "form",
                                buildUrl(res: any) {
                                    return res.url;
                                }
                            } as FsUploaderFormOptions
                        }
                    }
                },
                creator_name: {
                    title: "创建人",
                    type: "text",
                    column: {},
                    form: {
                        show: false,
                    },
                },
                create_datetime: {
                    title: "创建时间",
                    type: "datetime",
                    column: {},
                    form: {
                        show: false,
                    },
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
                buttons: {
                    add: { show: true },
                },
            },
            toolbar: {
                show: false,
                buttons: {
                    refresh: { show: false },
                    compact: { show: false },
                    export: { show: false },
                    columns: { show: false },
                },
            },
            table: {
                border: true,
                highlightCurrentRow: true,
            },
            rowHandle: {
                width: 180,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        show: true,
                        text: '详情',
                    },
                    remove: { text: '删除',
                        click: ({ row }: { row: TemplateRow }) => {
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
            form: {
                wrapper: {
                    is: 'el-dialog',
                    props: {
                        title: '编辑模板',
                        fullscreen: false,
                    },
                },
                beforeSubmit: ({ form }) => {
                    console.log('BeforeSubmit - form:', form);
                    if (form.template_type) {
                      // 确保只发送 id
                      console.log(form.template_type);
                      if(typeof form.template_type === "object"){
                        if(typeof form.template_type.name === "string"){
                            form.template_type = form.template_type.id;
                        }else{
                            form.template_type = form.template_type.name;
                        }
                      }
                      else{
                        form.template_type = form.template_type;
                      }
                    }
                    if (form.template_group) {
                        // 确保只发送 id
                        console.log(form.template_group);
                        if(typeof form.template_group === "object"){
                          if(typeof form.template_group.name === "string"){
                              form.template_group = form.template_group.id;
                          }else{
                              form.template_group = form.template_group.name;
                          }
                        }
                        else{
                          form.template_group = form.template_group;
                        }
                      }
                    return form;
                  }
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
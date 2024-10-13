import { 
    CrudOptions, 
    AddReq, 
    DelReq, 
    EditReq, 
    dict, 
    CrudExpose, 
    UserPageQuery, 
    CreateCrudOptionsRet 
  } from '@fast-crud/fast-crud';
  import * as api from './api';
  import { auth } from "/@/utils/authFunction";
  import { Modal, message, Button, Popconfirm } from 'ant-design-vue';
  import { ref, h } from 'vue';
  
  export default function createCrudOptions({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
      // 分页请求函数
      const pageRequest = async (query: UserPageQuery) => {
          try {
              // 修改为默认按 report_date 降序排序
              const finalQuery = { ...query, order_by: '-report_date' };
              const response = await api.GetList(finalQuery);
              return {
                  records: response.data,
                  total: response.total_items,
              };
          } catch (error) {
              message.error('获取简报列表失败');
              throw error;
          }
      };
  
      // 编辑请求函数
      const editRequest = async ({ form, row }: EditReq) => {
          if (row.id) form.id = row.id;
          return await api.UpdateObj(form);
      };
  
      // 删除请求函数，添加删除前确认
      const delRequest = async ({ row }: DelReq) => {
          return await api.DelObj(row.id);
      };
  
      // 添加请求函数
      const addRequest = async ({ form }: AddReq) => await api.AddObj(form);
  
      // 导出请求函数
      const exportRequest = async (query: UserPageQuery) => await api.exportReports(query);
  
      // 发送邮件请求函数
      const sendEmailRequest = async (id: number, recipients: string[]) => {
          try {
              await api.SendReport(id, recipients);
              message.success('邮件发送成功');
          } catch (error) {
              message.error('邮件发送失败');
              throw error;
          }
      };
  
      // 获取邮件历史请求函数
      const getEmailHistoryRequest = async (reportId: number) => {
          try {
              return await api.GetEmailHistory(reportId);
          } catch (error) {
              message.error('获取邮件历史失败');
              throw error;
          }
      };
  
      // 状态管理
      const isSendModalVisible = ref(false);
      const selectedReport = ref<any>(null);
      const recipientsInput = ref('');
  
      // 批量删除处理
      const handleBatchDelete = async () => {
          const selectedRows = crudExpose.crudProxy.getSelection();
          if (selectedRows.length === 0) {
              message.warning('请先选择要删除的简报');
              return;
          }
  
          Modal.confirm({
              title: '确认删除',
              content: `确定要删除选中的 ${selectedRows.length} 个简报吗？`,
              okText: '确认',
              cancelText: '取消',
              onOk: async () => {
                  try {
                      await Promise.all(selectedRows.map(row => api.DelObj(row.id)));
                      message.success('批量删除成功');
                      crudExpose.doRefresh();
                  } catch (error) {
                      message.error('批量删除失败');
                  }
              },
          });
      };
  
      // 打开发送邮件模态框
      const openSendEmailModal = (report: any) => {
          selectedReport.value = report;
          recipientsInput.value = '';
          isSendModalVisible.value = true;
      };
  
      // 处理发送邮件
      const handleSendEmail = async () => {
          if (!recipientsInput.value) {
              message.warning('请填写接收人邮件地址');
              return;
          }
          const recipients = recipientsInput.value.split(';').map(email => email.trim()).filter(Boolean);
          try {
              await sendEmailRequest(selectedReport.value.id, recipients);
              isSendModalVisible.value = false;
          } catch (error) {
              // 错误处理已在 sendEmailRequest 中处理
          }
      };
  
      // 打开发送历史模态框
      const openEmailHistoryModal = async (report: any) => {
          try {
              const history = await getEmailHistoryRequest(report.id);
              Modal.info({
                  title: '邮件发送历史',
                  content: h('div', [
                      history.email_history && history.email_history.length > 0
                          ? h('ul', history.email_history.map((record: any) => 
                              h('li', `发送时间: ${new Date(record.sent_at).toLocaleString()}, 
                                       接收者: ${record.recipients.join(', ')}, 
                                       状态: ${record.status}`)
                            ))
                          : h('p', '暂无发送历史记录。')
                  ]),
                  width: 600
              });
          } catch (error) {
              // 错误处理已在 getEmailHistoryRequest 中处理
          }
      };
  
      return {
          crudOptions: {
              request: {
                  pageRequest,
                  addRequest,
                  editRequest,
                  delRequest,
              },
              // 自定义搜索区域
              search: {
                  show: true,
                  showColumn: true, // 展示搜索条件
                  defaultSpan: 6, // 每个表单项占6列
                  collapse: true, // 收起多余的表单项
                  collapseSpan: 24,
                  // 修改日期选择器为范围选择
                  component: {
                      layout: 'inline',
                  },
                  // 自定义搜索按钮区域
                  searchButtonSpan: 18, // 调整按钮区域占位
                  showReset: false, // 隐藏重置按钮
                  actions: [
                      {
                          type: 'query',
                          text: '查询',
                          btnType: 'primary',
                          click: () => {
                              crudExpose.search();
                          }
                      },
                      {
                          type: 'button',
                          text: '批量删除',
                          btnType: 'danger',
                          disabled: () => crudExpose.crudProxy.getSelection().length === 0,
                          click: handleBatchDelete
                      }
                  ],
              },
              // 自定义操作栏
              toolbar: {
                  buttons: {
                      export: {
                          show: auth('ReportManagement:Export'),
                          text: "导出",
                          type: 'primary',
                          click: () => exportRequest(crudExpose.getSearchFormData())
                      },
                      add: {
                          show: auth('ReportManagement:Create'),
                          type: 'primary',
                      },
                      // 移除批量删除按钮
                  }
              },
              // 表格配置
              table: {
                  // 添加响应式布局支持
                  scroll: { x: 'max-content' },
                  // 启用排序
                  sorting: true,
              },
              rowHandle: {
                  fixed: 'right',
                  width: 200,
                  buttons: {
                      emailHistory: {
                          text: '邮件历史',
                          show: auth('ReportManagement:ViewEmailHistory'),
                          click: ({ row }) => openEmailHistoryModal(row)
                      },
                      remove: {
                          text: '删除',
                          show: auth('ReportManagement:Delete'),
                          type: 'danger',
                          // 使用 Popconfirm 进行删除确认
                          props: {
                              confirm: true,
                              title: '确认删除此简报吗？',
                              okText: '确认',
                              cancelText: '取消',
                          },
                      },
                  },
              },
              // 列配置
              columns: {
                  // 添加复选框列
                  _selection: {
                      title: '',
                      type: 'selection',
                      width: 50,
                      align: 'center',
                  },
                  type: {
                      title: '类型',
                      type: 'dict-select',
                      dict: dict({
                          url: '/api/reports/report_type/',
                          value: 'value',
                          label: 'label',
                      }),
                      search: {
                          show: true,
                          component: {
                              placeholder: '选择简报类型',
                              defaultValue: '日报', // 设置默认选中“日报”
                          },
                      },
                      column: {
                          minWidth: 100,
                          sortable: true,
                      },
                      form: {
                          rules: [{ required: true, message: '简报类型必选' }],
                          component: {
                              placeholder: '请选择简报类型',
                          },
                      },
                  },
                  title: {
                      title: '标题',
                      type: 'text',
                      search: {
                          show: true,
                          component: {
                              placeholder: '请输入简报标题',
                          },
                      },
                      column: {
                          minWidth: 200,
                          sortable: true,
                      },
                      form: {
                          rules: [{ required: true, message: '简报标题必填' }],
                          component: {
                              placeholder: '请输入简报标题',
                          },
                      },
                  },
                  summary: { // 新增摘要列
                      title: '摘要',
                      type: 'textarea',
                      search: {
                          show: false, // 根据需求，可以决定是否在搜索中显示
                      },
                      column: {
                          minWidth: 250,
                          ellipsis: true,
                      },
                      form: {
                          rules: [{ required: true, message: '摘要必填' }],
                          component: {
                              placeholder: '请输入摘要',
                              autoSize: { minRows: 3, maxRows: 6 },
                          },
                      },
                  },
                  report_date: {
                      title: '简报日期',
                      type: 'daterange', // 修改为日期范围选择器
                      search: { 
                          show: true,
                          component: {
                              placeholder: '选择简报日期范围',
                              format: 'YYYY-MM-DD',
                              valueFormat: 'YYYY-MM-DD',
                          },
                      },
                      form: {
                          rules: [{ required: true, message: '简报日期必填' }],
                          component: {
                              type: 'daterange',
                              placeholder: ['开始日期', '结束日期'],
                              format: 'YYYY-MM-DD',
                              valueFormat: 'YYYY-MM-DD',
                          }
                      },
                      column: {
                          width: 160,
                          component: { name: "format", format: "YYYY-MM-DD" },
                          sortable: true,
                      }
                  },
                  created_at: {
                      title: '创建时间',
                      type: 'datetime',
                      column: {
                          width: 180,
                          sortable: true,
                      },
                      form: {
                          show: false,
                      },
                  },
                  creator: {
                      title: '创建人',
                      type: 'number',
                      search: {
                          show: false,
                      },
                      column: {
                          width: 100,
                          sorter: true,
                      },
                      form: {
                          show: false,
                      },
                  },
                  // 根据需求，可以移除或调整其他列
              },
          },
          // 表单配置
          form: {
              async afterSubmit({ mode }) {
                  if (mode === 'add') {
                      message.success('添加成功');
                  } else if (mode === 'edit') {
                      message.success('编辑成功');
                  }
                  crudExpose.doRefresh();
              },
          },
          // 自定义组件部分
          components: {
              // 发送邮件模态框
              sendEmailModal: () => h(Modal, {
                  visible: isSendModalVisible.value,
                  title: `发送邮件 - ${selectedReport.value?.title || ''}`,
                  onOk: handleSendEmail,
                  onCancel: () => { isSendModalVisible.value = false; },
                  okText: '发送',
                  cancelText: '取消',
              }, {
                  default: () => h('div', [
                      h('a-input', {
                          type: 'textarea',
                          placeholder: '请输入接收人邮件地址，多个地址以;分隔',
                          vModel: {
                              value: recipientsInput.value,
                              callback: (val: string) => { recipientsInput.value = val; }
                          },
                          rows: 4,
                      }),
                  ])
              }),
          },
      };
  }
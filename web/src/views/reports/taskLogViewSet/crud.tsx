import { CreateCrudOptionsProps, CreateCrudOptionsRet, FsButton, dict } from "@fast-crud/fast-crud";
import { ElMessage, ElMessageBox } from 'element-plus';
import { create, getList, pause, remove, resume, update } from "./api";

export type TaskLog = {
  id?: number;
  job_id: string;
  task_name: string;
  start_time: string;
  end_time: string | null;
  result: string;
  parameters?: string;
  error_info?: string;
};

export default function ({ crudExpose }: CreateCrudOptionsProps<TaskLog>): CreateCrudOptionsRet<TaskLog> {

  const editRequest = ({ form, row }: { form: any, row: TaskLog }) => {
    if (form.id == null) {
      form.id = row.id;
    }
    const { id, ...updateData } = form;
    return update(id, updateData);
  }

  const rerunTask = (task: TaskLog) => {
    if (task.id) {
      resume(task.id).then(() => {
        ElMessage.success('任务已重新执行');
        crudExpose.doRefresh();
      }).catch(err => {
        ElMessage.error('重新执行失败: ' + err.message);
      });
    } else {
      ElMessage.error('无效的任务ID');
    }
  };

  const showTaskDetails = (row: TaskLog) => {
    const content = `
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
  .task-details-container {
    font-family: Arial, sans-serif;
    color: #333;
    width: 100%;
    line-height: 1.6;
    box-sizing: border-box;
  }
  .task-details-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
  }
  .task-details-table th, .task-details-table td {
    text-align: left;
    padding: 12px 15px;
    border-bottom: 1px solid #e0e0e0;
  }
  .task-details-table tr:last-child th,
  .task-details-table tr:last-child td {
    border-bottom: none;
  }
  .task-details-table th {
    background-color: #f7f7f7;
    font-weight: bold;
    width: 150px;
    color: #555;
  }
  .task-details-table td {
    background-color: #ffffff;
  }
  .no-error {
    color: #52c41a;
    font-weight: bold;
  }
  .error {
    color: #ff4d4f;
    font-weight: bold;
  }
  pre {
    background: #f5f5f5;
    padding: 12px;
    border-radius: 4px;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 0.9em;
    border: 1px solid #e0e0e0;
  }
  .task-title {
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 15px;
    color: #1890ff;
    text-align: center;
  }
  .button-container {
    text-align: center;
    margin-top: 20px;
  }
      </style>
      <div class="task-details-container">
        <div class="task-title">任务详情</div>
        <table class="task-details-table">
          <tr>
            <th>Job ID</th>
            <td>${row.job_id}</td>
          </tr>
          <tr>
            <th>任务名称</th>
            <td>${row.task_name}</td>
          </tr>
          <tr>
            <th>开始时间</th>
            <td>${row.start_time}</td>
          </tr>
          <tr>
            <th>结束时间</th>
            <td>${row.end_time || '<span class="error">未结束</span>'}</td>
          </tr>
          <tr>
            <th>运行参数</th>
            <td><pre>${JSON.stringify(row.parameters, null, 2)}</pre></td>
          </tr>
          <tr>
            <th>执行结果</th>
            <td>${row.result}</td>
          </tr>
          <tr>
            <th>错误信息</th>
            <td>${row.error_info ? `<span class="error">${row.error_info}</span>` : '<span class="no-error">无</span>'}</td>
          </tr>
        </table>
      </div>
    `;

    ElMessageBox({
      title: '',
      message: content,
      dangerouslyUseHTMLString: true,
      showCancelButton: true,
      confirmButtonText: '再次执行',
      cancelButtonText: '关闭',
      customClass: 'custom-message-box',
      beforeClose: (action, instance, done) => {
        if (action === 'confirm') {
          rerunTask(row);
        }
        done();
      }
    }).catch(() => {
      // 处理取消操作
    });
  };

  return {
    crudOptions: {
      request: {
        pageRequest: getList,
        addRequest: create,
        editRequest,
        delRequest: remove,
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
      columns: {
        job_id: {
          title: "job_id",
          type: "text",
        },
        task_name: {
          title: "任务名称",
          type: "text",
          search: { show: true },
        },
        start_time: {
          title: "开始时间",
          type: "datetime",
        },
        end_time: {
          title: "结束时间",
          type: "datetime",
        },
        result: {
          title: "执行结果",
          type: "dict-text",
        },
      },
      rowHandle: {
        width: 300,
        buttons: {
          view: {
            text: '详情',
            type: 'info',
            click: ({ row }: { row: TaskLog }) => {
              showTaskDetails(row);
            },
          },
          return: {
            text: '再次执行',
            type: 'primary',
            click: ({ row }: { row: TaskLog }) => {
              rerunTask(row);
            },
          },
          stop: {
            text: '停止',
            type: 'warning',
            click: ({ row }: { row: TaskLog }) => {
              if (row.id) {
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
<!-- src/components/TaskDetailsDialog.vue -->
<template>
    <el-dialog
      :visible.sync="visible"
      :title="title"
      width="600px"
      center
      @close="handleClose"
    >
      <el-descriptions column="1" border>
        <el-descriptions-item label="Job ID">{{ task.job_id }}</el-descriptions-item>
        <el-descriptions-item label="任务名称">{{ task.task_name }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ task.start_time }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ task.end_time || '未结束' }}</el-descriptions-item>
        <el-descriptions-item label="运行参数">
          <pre>{{ formattedParameters }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="执行结果">{{ task.result }}</el-descriptions-item>
        <el-descriptions-item label="错误信息">
          <span v-if="task.error_info">{{ task.error_info }}</span>
          <span v-else class="no-error">无</span>
        </el-descriptions-item>
      </el-descriptions>
  
      <span slot="footer" class="dialog-footer">
        <el-button @click="visible = false" type="primary">关闭</el-button>
      </span>
    </el-dialog>
  </template>
  
  <script lang="ts">
  import { defineComponent, computed } from 'vue';
import { TaskLog } from './crud';
  
  export default defineComponent({
    name: 'TaskDetailsDialog',
    props: {
      visible: {
        type: Boolean,
        required: true,
      },
      task: {
        type: Object as () => TaskLog,
        required: true,
      },
      title: {
        type: String,
        default: '任务详情',
      },
    },
    emits: ['update:visible'],
    setup(props, { emit }) {
      const handleClose = () => {
        emit('update:visible', false);
      };
  
      const formattedParameters = computed(() => {
        try {
          return JSON.stringify(JSON.parse(props.task.parameters || '{}'), null, 2);
        } catch {
          return props.task.parameters || '无';
        }
      });
  
      return {
        handleClose,
        formattedParameters,
      };
    },
  });
  </script>
  
  <style scoped>
  .no-error {
    color: #ff4d4f;
  }
  .dialog-footer {
    text-align: right;
  }
  pre {
    white-space: pre-wrap;
    word-break: break-all;
  }
  </style>
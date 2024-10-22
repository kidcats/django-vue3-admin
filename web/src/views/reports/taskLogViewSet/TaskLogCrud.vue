<!-- src/components/TaskLogCrud.vue -->
<template>
  <div>
    <FastCrud :crud-options="crudOptions" ref="crudRef" />

    <!-- 任务详情对话框 -->
    <TaskDetailsDialog
      :visible.sync="dialogVisible"
      :task="currentTask"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { useCrud } from "@fast-crud/fast-crud";
import crudOptionsFn, { TaskLog } from "./crud";
import TaskDetailsDialog from "./TaskDetailsDialog.vue";

const crudRef = ref();

const dialogVisible = ref(false);
const currentTask = ref<TaskLog | null>(null);

// 定义 view 回调函数
const handleView = (task: TaskLog) => {
  currentTask.value = task;
  dialogVisible.value = true;
};

// 获取 CRUD 选项，并传递 handleView 回调
const { crudOptions } = crudOptionsFn({
  crudExpose: {
    doRefresh: () => {
      crudRef.value?.reload();
    },
  },
  onView: handleView,
});
</script>

<style scoped>
/* 根据需要添加样式 */
</style>
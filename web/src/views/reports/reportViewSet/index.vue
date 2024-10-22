<!-- index.vue -->
<template>
	<fs-page class="PageFeatureSearchMulti">
	  <fs-crud ref="crudRef" v-bind="crudBinding">
		<template #cell_url="scope">
		  <el-tag size="small">{{ scope.row.url }}</el-tag>
		</template>
		<template #actionbar-right>
		  <importExcel api="api/reports/" v-auth="'user:Import'">导入</importExcel>
		</template>
	  </fs-crud>

	</fs-page>
  </template>
  
  <script lang="ts">
  import { onMounted, getCurrentInstance, defineComponent, ref } from 'vue';
  import { useFs } from '@fast-crud/fast-crud';
  import createCrudOptions from './crud';
  import importExcel from '/@/components/importExcel/index.vue'
  
  export default defineComponent({
	name: "reportViewSet",
	components: { importExcel },
	setup() {
	  const instance = getCurrentInstance();
	  const context: any = {
		componentName: instance?.type.name
	  };
  
	  const { crudBinding, crudRef, crudExpose, resetCrudOptions, showEmailHistory, emailHistoryData, emailHistoryDialogVisible } = useFs({ createCrudOptions, context });
  
	  // 页面打开后获取列表数据
	  onMounted(() => {
		crudExpose.doRefresh();
	  });
  
	  /**
	   * 关闭对话框时的处理
	   */
	  const onDialogClose = () => {
		// 清空邮件历史数据（可选）
		emailHistoryData.value = [];
	  };
  
	  return {
		crudBinding,
		crudRef,
		emailHistoryData,
		emailHistoryDialogVisible,
		onDialogClose,
	  };
	}
  });
  </script>

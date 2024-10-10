<template>
    <fs-page>
      <fs-crud ref="crudRef" v-bind="crudBinding">
        <template #actionbar-right>
          <el-button type="primary" @click="handleCreate">
            {{ t('crud.add') }}
          </el-button>
        </template>
      </fs-crud>
    </fs-page>
  </template>
  
  <script lang="ts">
  import { defineComponent, onMounted } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { useFs } from '@fast-crud/fast-crud';
  import createCrudOptions from './crud';
  
  export default defineComponent({
    name: 'ReportList',
    setup() {
      const { t } = useI18n();
      const { crudRef, crudBinding, crudExpose } = useFs({ createCrudOptions });
  
      onMounted(() => {
        crudExpose.doRefresh();
      });
  
      const handleCreate = () => {
        crudExpose.openAdd();
      };
  
      return {
        t,
        crudRef,
        crudBinding,
        handleCreate,
      };
    },
  });
  </script>
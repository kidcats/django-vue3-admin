<template>
    <fs-page class="ReportSettings">
        <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
            <a-tab-pane key="group" tab="模板分组">
                <fs-crud ref="groupCrudRef" v-bind="groupCrudBinding">
                    <template #actionbar-right>
                        <importExcel api="api/report-group/" v-auth="'report:Import'">导入分组</importExcel>
                    </template>
                </fs-crud>
            </a-tab-pane>
            <a-tab-pane key="type" tab="模板类型">
                <fs-crud ref="typeCrudRef" v-bind="typeCrudBinding">
                    <template #actionbar-right>
                        <importExcel api="api/report-type/" v-auth="'report:Import'">导入类型</importExcel>
                    </template>
                </fs-crud>
            </a-tab-pane>
        </a-tabs>
    </fs-page>
</template>

<script lang="ts">
import { onMounted, getCurrentInstance, defineComponent, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createGroupCrudOptions, createTypeCrudOptions } from './crud';
import importExcel from '/@/components/importExcel/index.vue';

export default defineComponent({
    name: "ReportSettings",
    components: { importExcel },
    setup() {
        const instance = getCurrentInstance();
        const activeTab = ref<string>('group');

        // 分组模块上下文
        const groupContext: any = {
            componentName: 'ReportGroup'
        };

        // 类型模块上下文
        const typeContext: any = {
            componentName: 'ReportType'
        };

        // 初始化分组模块的 CRUD
        const { 
            crudBinding: groupCrudBinding, 
            crudRef: groupCrudRef, 
            crudExpose: groupCrudExpose 
        } = useFs({ 
            createCrudOptions: createGroupCrudOptions, 
            context: groupContext 
        });

        // 初始化类型模块的 CRUD
        const { 
            crudBinding: typeCrudBinding, 
            crudRef: typeCrudRef, 
            crudExpose: typeCrudExpose 
        } = useFs({ 
            createCrudOptions: createTypeCrudOptions, 
            context: typeContext 
        });

        // 处理标签切换
        const handleTabChange = (key: string) => {
            if (key === 'group') {
                groupCrudExpose.doRefresh();
            } else if (key === 'type') {
                typeCrudExpose.doRefresh();
            }
        };

        // 页面加载后获取分组数据
        onMounted(() => {
            groupCrudExpose.doRefresh();
        });

        return {
            activeTab,
            groupCrudRef,
            groupCrudBinding,
            typeCrudRef,
            typeCrudBinding,
            handleTabChange
        };
    }
});
</script>

<style scoped>
.ReportSettings {
    .ant-tabs {
        margin: -24px;
        padding: 24px;
    }

    .ant-tabs-content {
        margin-top: 16px;
    }
}
</style>
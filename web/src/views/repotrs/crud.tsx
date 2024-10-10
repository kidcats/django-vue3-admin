import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import * as api from './api';
import { dict } from '@fast-crud/fast-crud';

export default function ({ expose }) {
  const { t } = useI18n();
  
  const pageRequest = async (query) => {
    return await api.getReportList(query);
  };

  const editRequest = async ({ form, row }) => {
    form.id = row.id;
    return await api.updateReport(form.id, form);
  };

  const delRequest = async ({ row }) => {
    return await api.deleteReport(row.id);
  };

  const addRequest = async ({ form }) => {
    return await api.createReport(form);
  };

  return {
    crudOptions: {
      request: {
        pageRequest,
        addRequest,
        editRequest,
        delRequest,
      },
      columns: {
        title: {
          title: t('report.title'),
          type: 'text',
          search: { show: true },
          form: { show: true },
        },
        type: {
          title: t('report.type'),
          type: 'dict-select',
          dict: dict({
            url: '/api/dict/report_types',
            value: 'value',
            label: 'label',
          }),
          search: { show: true },
          form: { show: true },
        },
        summary: {
          title: t('report.summary'),
          type: 'textarea',
          form: { show: true },
        },
        content: {
          title: t('report.content'),
          type: 'editor-quill',
          form: { show: true },
        },
        report_date: {
          title: t('report.reportDate'),
          type: 'date',
          search: { show: true },
          form: { show: true },
        },
      },
      rowHandle: {
        view: {
          click: (opts) => {
            expose.openDialog(opts.row.id);
          },
        },
      },
    },
  };
}
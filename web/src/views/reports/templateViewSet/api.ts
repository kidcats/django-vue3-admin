import { AddReq } from '@fast-crud/fast-crud';
import { getReportGroupList, ReportGroupRow, ReportTypeRow } from '../api';
import { request } from '/@/utils/service';

const BASE_URL = '/api/templates/';

export interface Template {
    id: number;
    template_type: ReportTypeRow;
    template_group: ReportGroupRow;
    template_name: string;
    content: string;
    creator_id: number;
    creator_name: string;
    create_datetime: string;
    update_datetime: string;
}

export interface TemplateQuery {
    page?: number;
    per_page?: number;
    name?: string;
    type?: string;
}

export const getList = (query: TemplateQuery) => {
    return request({
        url: `${BASE_URL}`,
        method: 'get',
        params: query
    });
};

export const getOne = (id: number) => {
    return request({
        url: `${BASE_URL}${id}/`,
        method: 'get'
    });
};

export const create = (data: AddReq) => {
    return request({
        url: BASE_URL,
        method: 'post',
        data
    });
};

export const update = (id: number, data: Partial<Template>) => {
    console.log(data);
    return request({
        url: `${BASE_URL}${id}/`,
        method: 'put',
        data
    });
};

export const remove = (id: number) => {
    return request({
        url: `${BASE_URL}${id}/`,
        method: 'delete'
    });
};

// 如果需要获取模板类型列表，可以添加以下方法
export const getTemplateTypes = () => {
    return request({
        url: `/api/reports/report_types/`,
        method: 'get'
    });
};

// 如果需要获取模板分组列表，可以添加以下方法
export const getTemplateGroups = () => {
    return getReportGroupList();
};
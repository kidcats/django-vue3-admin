import { request } from '/@/utils/service';

const BASE_URL = '/api/reports/';

export interface Report {
    id: number;
    title: string;
    content: string;
    report_type: string;
    status: string;
    creator: {
        id: number;
        username: string;
    };
    create_datetime: string;
    update_datetime: string;
}

export interface ReportQuery {
    page?: number;
    limit?: number;
    title__icontains?: string;
    report_type?: string;
    status?: string;
    create_datetime?: string;
    update_datetime?: string;
}

export const getList = (query: ReportQuery) => {
    return request({
        url: BASE_URL,
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

export const create = (data: Partial<Report>) => {
    return request({
        url: BASE_URL,
        method: 'post',
        data
    });
};

export const update = (id: number, data: Partial<Report>) => {
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

export const batchDelete = (ids: number[]) => {
    return request({
        url: BASE_URL,
        method: 'delete',
        data: { ids }
    });
};

export const sendReport = (id: number) => {
    return request({
        url: `${BASE_URL}${id}/send_report/`,
        method: 'post'
    });
};

export const getReportTypes = () => {
    return request({
        url: `${BASE_URL}report_types/`,
        method: 'get'
    });
};

export const getReportStatuses = () => {
    return request({
        url: `${BASE_URL}get_report_statuses/`,
        method: 'get'
    });
};
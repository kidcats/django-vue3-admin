import { getReportTypeList, ReportType } from '../api';
import { request } from '/@/utils/service';

const BASE_URL = '/api/email-configurations/';


export interface EmailConfiguration {
    id: number;
    report_type: ReportType;
    recipients: string;
    status: boolean;
    creator_id: number;
    create_datatime: string;
    updated_datatime: string;
}

export interface EmailConfigQuery {
    page?: number;
    per_page?: number;
    report_type?: string;
    status?: boolean;
    created_at?: string;
    updated_at?: string;
}

export const getList = (query: EmailConfigQuery) => {
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

export const create = (data: Partial<EmailConfiguration>) => {
    return request({
        url: BASE_URL,
        method: 'post',
        data
    });
};

export const update = (id: number, data: Partial<EmailConfiguration>) => {
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

export const updateStatus = (id: number, status: boolean) => {
    return request({
        url: `${BASE_URL}${id}/status/`,
        method: 'patch',
        data: { status }
    });
};


// 如果需要获取报告类型列表，可以添加以下方法
export const getReportTypes = async (): Promise<{ value: number; label: string }[]> => {
    try {
        const response = await getReportTypeList();
        if (response.data && Array.isArray(response.data.data)) {
            return response.data.data.map((item: ReportType) => ({
                value: item.id,
                label: item.name
            }));
        }
        return [];
    } catch (error) {
        console.error('Error fetching report types:', error);
        return [];
    }
};
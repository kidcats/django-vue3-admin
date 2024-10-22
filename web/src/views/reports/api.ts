import { request } from '/@/utils/service';

const FREQUENCY_URL = '/api/frequency';
const REPORT_GROUP_URL = '/api/report-group/';
const REPORT_TYPE_URL = '/api/report-type/';



// 核心模型类型（假设 CoreModel 包含这些字段）
export type CoreModelRow = {
    id: number;
    created_at: string;
    updated_at: string;
    creator:string;
};

// ReportType 模型对应的类型
export type ReportTypeRow = CoreModelRow & {
    id:number;
    name: string;
    description: string;
};

// ReportGroup 模型对应的类型
export type ReportGroupRow = CoreModelRow & {
    id:number;
    name: string;
    description: string;
};

// Frequency 模型对应的类型
export type FrequencyRow = CoreModelRow & {
    name: string;
    cron_expression: string;
    description: string;
    is_active: boolean;
};



// Interfaces
export interface Frequency {
    id: number;
    name: string;
    description: string;
    create_datetime: string;
    update_datetime: string;
}

export interface ReportGroup {
    id: number;
    name: string;
    description: string;
    create_datetime: string;
    update_datetime: string;
}

export interface ReportType {
    id: number;
    name: string;
    description: string;
    create_datetime: string;
    update_datetime: string;
}

export interface QueryParams {
    page?: number;
    per_page?: number;
    name?: string;
}

// Frequency API
export const getFrequencyList = () => {
    return request({
        url: FREQUENCY_URL,
        method: 'get'
    });
};

export const getFrequency = (id: number) => {
    return request({
        url: `${FREQUENCY_URL}${id}/`,
        method: 'get'
    });
};

export const createFrequency = (data: Partial<Frequency>) => {
    return request({
        url: FREQUENCY_URL,
        method: 'post',
        data
    });
};

export const updateFrequency = (id: number, data: Partial<Frequency>) => {
    return request({
        url: `${FREQUENCY_URL}${id}/`,
        method: 'put',
        data
    });
};

export const deleteFrequency = (id: number) => {
    return request({
        url: `${FREQUENCY_URL}${id}/`,
        method: 'delete'
    });
};

// Report Group API
export const getReportGroupList = () => {
    return request({
        url: REPORT_GROUP_URL,
        method: 'get'
    });
};

export const getReportGroup = (id: number) => {
    return request({
        url: `${REPORT_GROUP_URL}${id}/`,
        method: 'get'
    });
};

export const createReportGroup = (data: Partial<ReportGroup>) => {
    return request({
        url: REPORT_GROUP_URL,
        method: 'post',
        data
    });
};

export const updateReportGroup = (id: number, data: Partial<ReportGroup>) => {
    return request({
        url: `${REPORT_GROUP_URL}${id}/`,
        method: 'put',
        data
    });
};

export const deleteReportGroup = (id: number) => {
    return request({
        url: `${REPORT_GROUP_URL}${id}/`,
        method: 'delete'
    });
};

// Report Type API
export const getReportTypeList = () => {
    return request({
        url: REPORT_TYPE_URL,
        method: 'get'
    });
};

export const getReportType = (id: number) => {
    return request({
        url: `${REPORT_TYPE_URL}${id}/`,
        method: 'get'
    });
};

export const createReportType = (data: Partial<ReportType>) => {
    return request({
        url: REPORT_TYPE_URL,
        method: 'post',
        data
    });
};

export const updateReportType = (id: number, data: Partial<ReportType>) => {
    return request({
        url: `${REPORT_TYPE_URL}${id}/`,
        method: 'put',
        data
    });
};

export const deleteReportType = (id: number) => {
    return request({
        url: `${REPORT_TYPE_URL}${id}/`,
        method: 'delete'
    });
};
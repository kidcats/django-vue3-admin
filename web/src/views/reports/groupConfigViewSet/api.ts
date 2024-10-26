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

// api.ts

// 合并 ReportType 和 ReportGroup 的类型
export type ReportCategoryRow = CoreModelRow & {
    id: number;
    name: string;
    description: string;
    category_type: number;  // 添加类型标识字段
};

// 获取所有分类（包括类型和分组）
export const getReportCategories = async () => {
    // 并行请求两个接口
    const [typeRes, groupRes] = await Promise.all([
        request({
            url: REPORT_TYPE_URL,
            method: 'get'
        }),
        request({
            url: REPORT_GROUP_URL,
            method: 'get'
        })
    ]);

    // 合并数据并添加类型标识
    const types = typeRes.data.map((item: any) => ({
        ...item,
        category_type: 0
    }));
    
    const groups = groupRes.data.map((item: any) => ({
        ...item,
        category_type: 1
    }));

    return {
        data: [...types, ...groups],
        total: types.length + groups.length
    };
};

// 创建分类
export const createReportCategory = (data: Partial<ReportCategoryRow>) => {
    const url = data.form.category_type == 0 ? REPORT_TYPE_URL : REPORT_GROUP_URL;
    // 移除 category_type 字段，因为后端不需要
    const { category_type, ...submitData } = data.form;
    return request({
        url,
        method: 'post',
        data: submitData
    });
};

// 更新分类
export const updateReportCategory = (id: number, data: Partial<ReportCategoryRow>) => {
    const url = data.form.category_type == 0 ? REPORT_TYPE_URL : REPORT_GROUP_URL;
    // 移除 category_type 字段，因为后端不需要
    const { category_type, ...submitData } = data.form;
    return request({
        url: `${url}${id}/`,
        method: 'put',
        data: submitData
    });
};

// 删除分类
export const deleteReportCategory = (id: number, categoryType: number) => {
    console.log(categoryType);
    const url = categoryType == 0 ? REPORT_TYPE_URL : REPORT_GROUP_URL;
    return request({
        url: `${url}${id}/`,
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
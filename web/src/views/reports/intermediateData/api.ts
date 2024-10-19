import { request } from '/@/utils/service';

const BASE_URL = '/api/intermediate-data/';

export interface IntermediateData {
    id: number;
    date: string;
    internal_attacks: number;
    external_attacks: number;
    other_metrics: Record<string, any>;
    job: number;
    create_datetime: string;
    update_datetime: string;
}

export interface IntermediateDataQuery {
    page?: number;
    limit?: number;
    date?: string;
    job__name__icontains?: string;
    create_datetime?: string;
    update_datetime?: string;
}

export async function getList(query: IntermediateDataQuery) {
    return request({
        url: BASE_URL,
        method: 'get',
        params: query
    });
}

export async function getOne(id: number) {
    return request({
        url: `${BASE_URL}${id}/`,
        method: 'get'
    });
}

export async function create(data: Partial<IntermediateData>) {
    return request({
        url: BASE_URL,
        method: 'post',
        data
    });
}

export async function update(id: number, data: Partial<IntermediateData>) {
    return request({
        url: `${BASE_URL}${id}/`,
        method: 'put',
        data
    });
}

export async function remove(id: number) {
    return request({
        url: `${BASE_URL}${id}/`,
        method: 'delete'
    });
}

// 如果你想保持原来的对象结构，也可以这样导出
export const intermediateDataApi = {
    getList,
    getOne,
    create,
    update,
    remove
};
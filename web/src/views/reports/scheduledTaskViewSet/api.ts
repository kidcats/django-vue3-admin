import { request } from '/@/utils/service';
import { Frequency, FrequencyRow, getFrequencyList, getReportTypeList } from '../api';
import { Template } from '../templateViewSet/api';

const BASE_URL = '/api/scheduled-tasks/';

export interface ScheduledTask {
    id: number;
    name: string;
    frequency: FrequencyRow;
    status: string;
    create_datetime: string;
    update_datetime: string;
    template:Template;
    // 添加其他必要的字段
}

export interface ScheduledTaskQuery {
    page?: number;
    limit?: number;
    name__icontains?: string;
    frequency__name?: string;
    status?: string;
    create_datetime?: string;
    update_datetime?: string;
}

export async function getList(query: ScheduledTaskQuery) {
    const t = request({
        url: `${BASE_URL}`,
        method: 'get',
        params: query
    });
    console.log("helo,{}",t);
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

export async function create(data: Partial<ScheduledTask>) {
    return request({
        url: BASE_URL,
        method: 'post',
        data
    });
}

export async function update(id: number, data: Partial<ScheduledTask>) {
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

export async function pause(id: number) {
    return request({
        url: `${BASE_URL}${id}/pause/`,
        method: 'patch'
    });
}

export async function resume(id: number) {
    return request({
        url: `${BASE_URL}${id}/resume/`,
        method: 'patch'
    });
}


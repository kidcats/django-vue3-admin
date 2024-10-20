import { request } from '/@/utils/service';

const BASE_URL = '/api/task-logs/';

export interface TaskLog {
    id: number;
    job_id: string;
    task_name: string;
    start_time: string;
    end_time: string | null;
    result: string;
    parameters: Record<string, any>;
    error_info: string;
    create_datetime: string;
    update_datetime: string;
}

export interface TaskLogQuery {
    page?: number;
    limit?: number;
    job_id__icontains?: string;
    task_name__icontains?: string;
    result?: string;
    create_datetime?: string;
    update_datetime?: string;
}

export async function getList(query: TaskLogQuery) {
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

export async function create(data: Partial<TaskLog>) {
    return request({
        url: BASE_URL,
        method: 'post',
        data
    });
}

export async function update(id: number, data: Partial<TaskLog>) {
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

// 如果你想保持原来的对象结构，也可以这样导出
export const taskLogApi = {
    getList,
    getOne,
    create,
    update,
    remove,
    pause,
    resume,
};
import { request } from '/@/utils/request';

const apiPrefix = '/api/reports/';

export function getReportList(query: any) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query,
  });
}

export function getReportDetail(id: string) {
  return request({
    url: `${apiPrefix}${id}/`,
    method: 'get',
  });
}

export function createReport(data: any) {
  return request({
    url: apiPrefix,
    method: 'post',
    data,
  });
}

export function updateReport(id: string, data: any) {
  return request({
    url: `${apiPrefix}${id}/`,
    method: 'put',
    data,
  });
}

export function deleteReport(id: string) {
  return request({
    url: `${apiPrefix}${id}/`,
    method: 'delete',
  });
}

export function sendReport(id: string, recipients: string[]) {
  return request({
    url: `${apiPrefix}${id}/send/`,
    method: 'post',
    data: { recipients },
  });
}

export function getEmailHistory(id: string) {
  return request({
    url: `${apiPrefix}${id}/email-history/`,
    method: 'get',
  });
}
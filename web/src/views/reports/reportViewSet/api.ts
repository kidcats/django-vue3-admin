import { request } from '/@/utils/service';


// 获取所有简报类型
export function GetReportTypes() {
  return request({
      url: '/api/reports/report_type/',
      method: 'get',
  });
}

// 获取简报列表
export function GetList(query: any) {
  return request({
    url: '/api/reports',
    method: 'get',
    params: query
  });
}

// 创建新简报
export function AddObj(obj: any) {
  return request({
    url: '/api/reports',
    method: 'post',
    data: obj
  });
}

// 获取特定简报详情
export function GetReport(id: number) {
  return request({
    url: `/api/reports/${id}`,
    method: 'get'
  });
}

// 更新简报信息
export function UpdateObj(obj: any) {
  return request({
    url: `/api/reports/${obj.id}`,
    method: 'put',
    data: obj
  });
}

// 删除简报
export function DelObj(id: number) {
  return request({
    url: `/api/reports/${id}`,
    method: 'delete'
  });
}

// 发送简报邮件
export function SendReport(id: number, recipients: string[]) {
  return request({
    url: `/api/reports/${id}/send`,
    method: 'post',
    data: { recipients }
  });
}

// 获取邮件发送历史
export function GetEmailHistory(reportId: number) {
  return request({
    url: `/api/reports/${reportId}/email-history`,
    method: 'get'
  });
}

// （可选）导出简报
export function exportReports(query: any) {
  return request({
    url: '/api/reports/export',
    method: 'get',
    params: query,
    responseType: 'blob'
  });
}
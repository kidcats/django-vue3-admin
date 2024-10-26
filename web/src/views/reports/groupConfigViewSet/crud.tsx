// crud.ts
import { dict } from '@fast-crud/fast-crud';
import * as api from './api';

export const createGroupCrudOptions = (context: any) => {
    return {
        request: {
            pageRequest: api.getReportGroupList,
            addRequest: api.createReportGroup,
            editRequest: api.updateReportGroup,
            delRequest: api.deleteReportGroup
        },
        columns: {
            id: {
                title: 'ID',
                type: 'number',
                column: {
                    width: 50
                },
                form: {
                    show: false
                }
            },
            name: {
                title: '分组名称',
                type: 'text',
                search: {
                    show: true
                },
                form: {
                    rules: [
                        { required: true, message: '请输入分组名称' }
                    ]
                }
            },
            description: {
                title: '描述',
                type: 'text',
                column: {
                    width: 300,
                    showOverflowTooltip: true
                }
            },
            created_at: {
                title: '创建时间',
                type: 'datetime',
                column: {
                    width: 180
                },
                form: {
                    show: false
                }
            },
            updated_at: {
                title: '更新时间',
                type: 'datetime',
                column: {
                    width: 180
                },
                form: {
                    show: false
                }
            },
            creator: {
                title: '创建人',
                type: 'text',
                form: {
                    show: false
                }
            }
        }
    };
};

export const createTypeCrudOptions = (context: any) => {
    return {
        request: {
            pageRequest: api.getReportTypeList,
            addRequest: api.createReportType,
            editRequest: api.updateReportType,
            delRequest: api.deleteReportType
        },
        columns: {
            id: {
                title: 'ID',
                type: 'number',
                column: {
                    width: 50
                },
                form: {
                    show: false
                }
            },
            name: {
                title: '类型名称',
                type: 'text',
                search: {
                    show: true
                },
                form: {
                    rules: [
                        { required: true, message: '请输入类型名称' }
                    ]
                }
            },
            description: {
                title: '描述',
                type: 'text',
                column: {
                    width: 300,
                    showOverflowTooltip: true
                }
            },
            created_at: {
                title: '创建时间',
                type: 'datetime',
                column: {
                    width: 180
                },
                form: {
                    show: false
                }
            },
            updated_at: {
                title: '更新时间',
                type: 'datetime',
                column: {
                    width: 180
                },
                form: {
                    show: false
                }
            },
            creator: {
                title: '创建人',
                type: 'text',
                form: {
                    show: false
                }
            }
        }
    };
};
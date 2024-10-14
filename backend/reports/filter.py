import operator
import re
from collections import OrderedDict
from functools import reduce

import six
from django.db import models
from django.db.models import Q, F
from django.db.models.constants import LOOKUP_SEP
from django_filters import utils, FilterSet
from django_filters.constants import ALL_FIELDS
from django_filters.filters import CharFilter, DateTimeFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.utils import get_model_field
from rest_framework.filters import BaseFilterBackend
from django_filters.conf import settings
from dvadmin.system.models import Dept, ApiWhiteList, RoleMenuButtonPermission
from dvadmin.utils.models import CoreModel


class ReportsCoreModelFilterBankend(BaseFilterBackend):
    """
    自定义时间范围过滤器
    """
    def filter_queryset(self, request, queryset, view):
        print(request.query_params)
        create_datetime_after = request.query_params.get('create_datetime[0]', None)
        create_datetime_before = request.query_params.get('create_datetime[1]', None)
        # update_datetime_after = request.query_params.get('update_datetime_after', None)
        # update_datetime_before = request.query_params.get('update_datetime_after', None)
        if any([create_datetime_after, create_datetime_before,]):
            create_filter = Q()
            if create_datetime_after and create_datetime_before:
                create_filter &= Q(create_datetime__gte=create_datetime_after) & Q(create_datetime__lte=create_datetime_before)
            elif create_datetime_after:
                create_filter &= Q(create_datetime__gte=create_datetime_after)
            elif create_datetime_before:
                create_filter &= Q(create_datetime__lte=create_datetime_before)

            # 更新时间范围过滤条件
            # update_filter = Q()
            # if update_datetime_after and update_datetime_before:
            #     update_filter &= Q(update_datetime__gte=update_datetime_after) & Q(update_datetime__lte=update_datetime_before)
            # elif update_datetime_after:
            #     update_filter &= Q(update_datetime__gte=update_datetime_after)
            # elif update_datetime_before:
            #     update_filter &= Q(update_datetime__lte=update_datetime_before)
            # 结合两个时间范围过滤条件
            queryset = queryset.filter(create_filter)
            return queryset
        return queryset
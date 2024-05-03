from rest_framework.pagination import PageNumberPagination
from common.custom_response import CustomResponse


class GeneralPage(PageNumberPagination):
    """
    通用分页类
    """
    page_size = 10  # 每页显示数量
    max_page_size = 200  # 最多能设置的每页显示数量
    page_query_param = 'page'  # 页码的参数名称
    page_size_query_param = 'page_size'  # 页码的参数名称

    def get_paginated_response(self, data):
        """
        重写get_paginated_response()方法
        """
        return CustomResponse(
            data=data,
            code=200,
            msg='OK',
            total=self.page.paginator.count,
            next=self.get_next_link(),
            previous=self.get_previous_link()
        )


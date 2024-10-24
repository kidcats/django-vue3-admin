from reports.models import Template

class TemplateService:
    """
    模板服务类,处理模板相关的业务逻辑
    """
        

    def get_template(self, id:int):
        """
        获取指定类型和分组的模板
        """
        try:
            template = Template.objects.get(
                id=id,
            )
            return template
        except Template.DoesNotExist:
            raise ValueError(f"Template not found for type: {template_type} and group: {template_group}")
    
    @staticmethod
    def validate_template_content(content):
        """验证模板内容是否合法"""
        try:
            # 允许使用的变量列表
            allowed_variables = {
                "external_attack_time_range",
                "external_attack_total",
                "previous_external_attack_total",
                "percentage_change",
                "external_anomalous_attack_total"
            }
            
            # 提取模板中使用的所有变量
            import re
            used_variables = set(re.findall(r'\{\{(\w+)\}\}', content))
            
            # 检查使用的变量是否都在允许列表中
            invalid_variables = used_variables - allowed_variables
            if invalid_variables:
                raise ValueError(f"使用了未定义的变量: {', '.join(invalid_variables)}")

            # 检查条件语句的完整性
            if content.count('{%if') != content.count('{%endif%}'):
                raise ValueError("if/endif语句不匹配")

            # 检查else语句是否在if语句内
            if '{%else%}' in content:
                if content.count('{%else%}') > content.count('{%if'):
                    raise ValueError("else语句必须在if语句内")

            return True, None
        except ValueError as e:
            return False, str(e)

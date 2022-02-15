from django.core.exceptions import ObjectDoesNotExist


def get_model_object(model, column_name, column_value, **kwargs):
    manager_query = kwargs.get('manager_query', model.objects)
    error_response = kwargs.get('custom_error',
                                f"{column_name} {column_value} "
                                f"was not found in the "
                                f"{model.__name__}'s table.")
    try:
        model_instance = manager_query.get(**{column_name: column_value})
        return model_instance
    except ObjectDoesNotExist:
        return error_response or 'Object was not found!'


def get_query_set(model, organization, **kwargs):
    manager_query = kwargs.get('manager_query', model.objects)
    order_by = kwargs.get('order_by', 'created_at')
    distinct_qs = kwargs.get('distinct_qs', False)
    if distinct_qs:
        return manager_query.filter(organization=organization).distinct(distinct_qs).all()
    else:
        query_list = manager_query.filter(organization=organization).order_by(order_by)
        return query_list


def check_exists(name, model, value):
    if value is not None or value != '':
        query = {name: value}
        if get_query_set(model).filter(**query).exists():
            return True
        else:
            return False

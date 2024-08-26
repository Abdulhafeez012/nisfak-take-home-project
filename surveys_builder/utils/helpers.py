def evaluate_condition(condition, section_field_map):
    """
    Evaluate a condition and return the result
    """
    for dependency in condition.dependencies.all():
        source_field = dependency.source_field
        target_field = dependency.target_field
        dependency_type = dependency.dependency_type
        source_value = section_field_map.get(source_field.id)
        target_value = section_field_map.get(target_field.id)
        if not source_value or not target_value:
            return False
        if dependency_type == 'equal':
            if source_value != target_value:
                return False
        elif dependency_type == 'not_equal':
            if source_value == target_value:
                return False
    return True


def get_section_field_map(response_data):
    """
    Get a map of section field ids to field values
    """
    section_field_map = {}
    for section in response_data['sections']:
        for field in section['fields']:
            section_field_map[field['id']] = field['value']
    return section_field_map


def check_dependency(field, dependent_field_value):
    """
    Check if a field dependency is met
    """
    if field['dependency_type'] == 'equal':
        return field['value'] == dependent_field_value
    elif field['dependency_type'] == 'does_not_equal':
        return field['value'] != dependent_field_value
    elif field['dependency_type'] == 'greater_than':
        return field['value'] > dependent_field_value
    elif field['dependency_type'] == 'less_than':
        return field['value'] < dependent_field_value
    elif field['dependency_type'] == 'greater_than_or_equal':
        return field['value'] >= dependent_field_value
    elif field['dependency_type'] == 'less_than_or_equal':
        return field['value'] <= dependent
    elif field['dependency_type'] == 'contains':
        return field['value'] in dependent_field_value
    elif field['dependency_type'] == 'not_contains':
        return field['value'] not in dependent_field_value
    elif field['dependency_type'] == 'is_true':
        return field['value'] is True
    elif field['dependency_type'] == 'is_false':
        return field['value'] is False
    else:
        return False

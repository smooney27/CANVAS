from django.forms import ValidationError

def validate_impediment(value):
    # valid values for an impediment are null (not completed yet), 
    # 0 (other), 1 (blocked), 2 (too far), 3 (too blurry), 4 (too dim)
    if (value != None and value > 4):
        raise ValidationError("Invalid value for impediment!")

def validate_boolean(value):
    # valid values for a boolean are null (not completed yet), 
    # 0 (false), 1 (true), 2(unknown)
    if (value != None and value > 2):
        raise ValidationError("Invalid value for boolean field!")

def validate_category(value):
    # todo$ Should really be doing category-specific validation
    if (value != None and (value < -2 or value > 1000)):
        raise ValidationError("Please select a choice from the radio buttons")

def validate_task_allocation(value):
    if (value == None or value > 2):
        raise ValidationError("Please select a task allocation strategy")

def validate_task_overlap(value):
    if (value != None and value > 100):
        raise ValidationError("Please enter a value between 0 and 100")

def coerce_string_integer(value):
    try: 
        int_value = int(value)
    except TypeError:
        return None
    return int_value

def coerce_boolean(value):
    int_value = coerce_string_integer(value)
    if (int_value < 0 or int_value > 2):
        return None
    else:
        return int_value

def coerce_impediment(value):
    int_value = coerce_string_integer(value)
    if (int_value < 0 or int_value > 4):
        return None
    else:
        return int_value

def coerce_category(value):
    int_value = coerce_string_integer(value)
    # todo$ same issue as with validate.
    if (int_value < -2 or int_value > 1000):
        return None
    else:
        return int_value

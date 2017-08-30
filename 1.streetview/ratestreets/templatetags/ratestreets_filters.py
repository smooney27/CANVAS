from django import template
import logging

register = template.Library()

@register.filter
def completed_tasks_for_user(object, user):
    return object.completed_tasks(user=user)

def do_invoke(parser, token):
    try:
        tokens = token.split_contents()
        object = tokens[1]
        method_name = tokens[2]
        if len(tokens) > 3:
            kwargs_array = tokens[3:]
        else:
            kwargs_array = []
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires an object, a method name and a list of kwargs" % token.contents.split()[0]
    return InvokeNode(object.rstrip(','), method_name.rstrip(','), kwargs_array)
#    return InvokeNode

class InvokeNode(template.Node):
    def __init__(self, object, method_name, kwargs_array):
        self.object = template.Variable(object)
        self.method_name = method_name
        self.kwargs = {}
        for kwargs_pair in kwargs_array:
            kwargs_pair_array = kwargs_pair.split('=')
            self.kwargs[kwargs_pair_array[0]] = template.Variable(kwargs_pair_array[1].rstrip(','))
    def render(self, context):
        method = getattr(self.object.resolve(context), self.method_name)
        if (method == None):
            raise template.TemplateSyntaxError, "%s method not found on object %s" % (method, object)
        # resolve all kwargs values, too.
        kwargs_resolved = {}
        for kwarg_name, kwarg_value in self.kwargs.iteritems():
            kwargs_resolved[str(kwarg_name)] = kwarg_value.resolve(context)
        return method(**kwargs_resolved)

register.tag('invoke', do_invoke)
#
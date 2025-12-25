from django import template

register = template.Library()

@register.filter
def get_option(question, opt):
    return getattr(question, f"option_{opt.lower()}")


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
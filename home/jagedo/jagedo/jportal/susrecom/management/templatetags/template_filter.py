from django import template
register = template.Library()


@register.filter
def in_pics(pics, items):
     return pics.filter(product=items)




#  {% if pics %}
#                     {% for pic in pics|in_pics:x.id %}
#                     {{ pic.id}}
#                     <!-- <img src="/media/{{ pic.cover }}" class="img-thumbnail" loading="lazy"> -->
#                   {% endfor %}

#                   {% endif %}



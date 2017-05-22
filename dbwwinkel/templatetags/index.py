from django import template

register = template.Library()


@register.filter
def index(List, i):
    try:
        return List[int(i)]
    except:
        return None


@register.filter
def question_regional_user(question,user):
    region_user = user.as_manager().region.all()
    region_question = question.region.all()

    if region_user & region_question:
        return True

    return False



from django.conf import settings
from path import path


def run():
    template_path = path(__file__).dirname() / 'templates'
    settings.TEMPLATE_DIRS.append(template_path)
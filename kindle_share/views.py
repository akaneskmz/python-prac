from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from kindle_share.models import KindleShare


class AddView(View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        content = request.body.decode()
        KindleShare(add_date=timezone.now(), content=content).save()

        return HttpResponse("OK")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddView, self).dispatch(*args, **kwargs)
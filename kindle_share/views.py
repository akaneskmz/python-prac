from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


class AddView(View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        content = request.body.decode()
        print(content)

        return HttpResponse("OK")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddView, self).dispatch(*args, **kwargs)
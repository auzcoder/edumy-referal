from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.shortcuts import render



class TableView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


def waiting_view(request):
    """
    View for users waiting for admin verification.
    """
    return render(request, "waiting.html", {"user": request.user})

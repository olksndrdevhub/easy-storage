from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView, View

from companies.models import Company
# Create your views here.


class CreateCompanyView(View):
    template_name = "create-company.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        self.template_name = "partials/create-company-form.html"
        context = {}

        name = request.POST.get("name", None)
        description = request.POST.get("description", None)

        if not name or name.strip() == "":
            context["submitted_description"] = description
            context["name_error"] = "Company name is required!"
            messages.add_message(request, messages.ERROR, "Company name is required!")
            return render(request, self.template_name, context)

        new_company = Company.objects.create(name=name.strip(), description=description)
        messages.add_message(request, messages.SUCCESS, "Company created successfully!")
        response = HttpResponse(status=201)
        response["HX-Location"] = reverse(
            "companies:company", kwargs={"slug": new_company.slug}
        )
        return response


class CompaniesView(TemplateView):
    template_name = "companies.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["companies"] = Company.objects.all()
        return context


class CompanyView(View):
    template_name = "company.html"

    def get(self, request, slug):
        context = {}

        company = Company.objects.get(slug=slug)
        context["company"] = company

        return render(request, self.template_name, context)

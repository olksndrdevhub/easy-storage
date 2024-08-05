from django.shortcuts import redirect, render

from companies.models import Company, CompanyMemership

# Create your views here.


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("signin_view")
    context = {}

    company_memberships = CompanyMemership.objects.filter(
        user=request.user
    ).values_list("company", flat=True)
    context["companies"] = Company.objects.filter(id__in=company_memberships)
    print(context)

    return render(request, "index.html", context)

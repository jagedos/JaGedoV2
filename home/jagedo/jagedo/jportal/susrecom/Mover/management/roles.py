from django.shortcuts import render
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
import json
from accounts.models import CustomUser, CompanyMeta, Counties
from management.models import Modules, UserTypes, Permissions, Actions
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta, date, time, timezone
from django.db.models import Q


# Create your views here.
class UsertypesDataTableView(BaseDatatableView):
    columns = ["name", "status"]

    def get_initial_queryset(self):
        queryset = UserTypes.objects.all()
        return queryset


def index(request):
    template = loader.get_template("users/roles/utypes.html")
    context = {
        "cats": 1,
    }
    return HttpResponse(template.render(context, request))


def addrecord(request):
    x = request.POST["name"]

    member = UserTypes(name=x)
    member.save()
    response = {"success": "Data Added successfully."}
    return JsonResponse(response)


def edita(request, id):
    mymember = model_to_dict(UserTypes.objects.get(id=id))

    response = mymember

    return JsonResponse(response, safe=False)


def updaterecord(request):
    x = request.POST["name"]
    id = request.POST["hidden_id"]

    member = UserTypes.objects.get(id=id)
    member.name = x
    member.save()
    response = {"success": "Data Updated successfully."}
    return JsonResponse(response)


def delete(request, id):
    # check if there is a user with this role
    member = CustomUser.objects.filter(usertype=id)
    if member:
        response = {
            "success": "You cannot delete this role because it is in use by a user."
        }
        return JsonResponse(response)

    member = UserTypes.objects.get(id=id)
    member.delete()

    response = {"success": "Data Deleted successfully."}
    return JsonResponse(response)


def rolesedit(request, id):
    actions = Actions.objects.all()
    permissions = Permissions.objects.filter(user_type__id=id)
    permitted_actions = {p.action.id: p.status for p in permissions if p.action}

    roles_data = []
    for action in actions:
        roles_data.append(
            {
                "action_id": action.id,
                "action_name": action.name,
                "module_name": action.module.name,
                "has_permission": permitted_actions.get(action.id, False),
            }
        )

    return JsonResponse({"roles": roles_data, "id": id})


@csrf_exempt
def rolesupdate(request):
    if request.method == "POST":
        data = request.POST
        user_type_id = data.get("hidd_id")

        # Assuming action IDs are prefixed with 'action_' in the form
        action_ids = [
            key.replace("action_", "")
            for key in data.keys()
            if key.startswith("action_")
        ]

        # Get all possible actions
        all_actions = Actions.objects.all()

        for action in all_actions:
            try:
                # Check if permission already exists
                permission = Permissions.objects.get(
                    user_type=user_type_id, action=action
                )

                # Update status based on whether checkbox was checked
                if (
                    str(action.id) in action_ids
                ):  # Convert to string because action_ids elements are strings
                    permission.status = True
                else:
                    permission.status = False

                permission.save()

            except Permissions.DoesNotExist:
                # If checkbox was checked and permission doesn't exist, create new permission
                if str(action.id) in action_ids:
                    Permissions.objects.create(
                        user_type_id=user_type_id, action=action, status=True
                    )

        return JsonResponse({"success": "Permissions updated successfully!"})

    return JsonResponse({"errors": "Invalid request method!"})

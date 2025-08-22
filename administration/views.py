import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, CreateView
from django.core.exceptions import ObjectDoesNotExist

from .models import SiteGroup
from tableviewer.models import DynamicTable
from .utils import *
from .forms import SiteGroupForm, AddUserForm


class GroupsView(LoginRequiredMixin, View):
    title = "My Groups"
    template_name = 'administration/groups/groups.html'

    def get(self, request, *args, **kwargs):
        user_groups = SiteGroup.objects.filter(owners=request.user)
        context = {
            'title': self.title,
            'user_groups': user_groups
        }
        return render(request, self.template_name, context)


class AddGroupView(LoginRequiredMixin, View):
    title = "Add Group"
    template_name = 'administration/groups/add_group.html'
    action = "add"

    def get(self, request, *args, **kwargs):
        form = SiteGroupForm()
        context = {
            'title': self.title,
            'form': form,
            'action': self.action,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = SiteGroupForm(request.POST)
        if form.is_valid():
            group = form.save()

            # Add the user to members
            group.members.add(request.user)

            # Optionally, add the user to owners too
            group.owners.add(request.user)

            return redirect(reverse_lazy('administration:groups'))
        else:
            context = {
                'title': self.title,
                'form': form,
            }
            return render(request, self.template_name, context)


class EditGroupView(LoginRequiredMixin, View):
    title = "Edit Group"
    template_name = 'administration/groups/add_group.html'
    success_template_name = 'administration/view_group.html'
    action = "edit"

    def get(self, request, pk, *args, **kwargs):
        instance = SiteGroup.objects.get(pk=pk)
        form = SiteGroupForm(instance=instance)
        context = {
            'title': self.title,
            'form': form,
            'action': self.action,
            'instance': instance,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        instance = SiteGroup.objects.get(pk=pk)
        form = SiteGroupForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('administration:view-group', kwargs={'pk': pk}))
        else:
            context = {
                'title': self.title,
                'form': form,
                'action': self.action,
                'instance': SiteGroup.objects.get(pk=pk),
            }
            return render(request, self.template_name, context)


class ViewGroupView(LoginRequiredMixin, View):
    title = ""
    template_name = 'administration/groups/view_group.html'

    def get(self, request, pk, *args, **kwargs):
        group = SiteGroup.objects.get(pk=pk)
        self.title = group.name
        context = {
            'title': self.title,
            'group': group
        }
        return render(request, self.template_name, context)


class AdministrationView(View):
    title = "Administration"
    template_name = 'administration/administration.html'

    def get(self, request, *args, **kwargs):
        groups = SiteGroup.objects.all()
        users = User.objects.all()
        tables = DynamicTable.objects.all()

        context = {
            'title': self.title,
            'groups': groups,
            'users': users,
            'tables': tables,
        }
        return render(request, self.template_name, context)


class UserAddView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('user-login')
    model = User
    form_class = AddUserForm
    template_name = 'administration/users/add_user.html'
    success_url = reverse_lazy('users-list')

    def get_context_data(self, **kwargs):
        context = super(UserAddView, self).get_context_data(**kwargs)
        context['title'] = 'Add User'
        context['action'] = 'Add'
        # context['cancel_url'] = self.request.META.get('HTTP_REFERER')
        # support form data
        # user = self.request.user
        # if user.is_anonymous:
        #     context['support_form'] = SupportForm(initial={'url': self.request.path})
        # else:
        #     context['support_form'] = SupportForm(initial={
        #         'name': f'{user.first_name} {user.last_name}',
        #         'email': user.email,
        #         'url': self.request.path,
        #     })
        return context

    # setting unusable password for added users
    def form_valid(self, form):
        # create the new user
        user = create_user(form)
        messages.success(self.request, 'User created!')
        return redirect(reverse_lazy('administration:index'))


# ## Group Fetch Calls ##
def add_user_to_group(request):
    search_by = request.GET.get('search_by', None)
    if search_by:
        pass


# ##### Fetch calls related to retrieving users #####
def change_user_membership(request):
    user_pk = request.GET.get('user_id', None)  # getting the pk from the payload
    group_pk = request.GET.get('group_id', None)  # retrieving the group's pk from payload
    change_type = request.GET.get('change_type', None)  # add or remove
    membership = request.GET.get('membership', None)  # owner or member
    full_remove = request.GET.get('full_remove')  # when removing user as owner, if they would like to remove them as member too
    user_data = {
        "user_id": user_pk,
        "group_id": group_pk,
        "change_type": change_type,
        "membership": membership,
        "full_remove": full_remove == 'True'
    }
    try:
        # making sure the pk is present
        if user_pk is None or group_pk is None:
            raise ValueError("Owner or Member pk is none")

        user = User.objects.get(pk=user_pk)  # getting the user instance
        group = SiteGroup.objects.get(pk=group_pk)  # getting the SiteGroup instance

        try:
            # applying the requested change
            change_member_membership(user, group, change_type=change_type, membership=membership)
            # creating a dictionary of the user instance
            user_dict = user.__dict__
            user_dict.pop('_state')  # removing state because what the hell even is that
            user_dict.pop('password')  # removing the password for obvious reasons.

            context = {
                "success": True,
                "user": user_dict,
                "user_data": user_data
            }
            return JsonResponse(context, safe=False)
        except ValueError as e:
            raise ValueError(e)
    except ValueError as e:
        return JsonResponse({'error': str(e), 'status': "error", 'user_data': user_data})
    except User.DoesNotExist or SiteGroup.DoesNotExist as e:
        return JsonResponse({'error': str(e), 'status': "error"})


# ## LDAP Fetch Calls ##
def fetch_ldap_users(request):
    ldapi = Ldap()
    query_param = request.GET.get("q")
    if query_param is not None or query_param != "":
        user_data = ldapi.get_users(query_param)
        if user_data[0]:
            return JsonResponse(user_data[1], safe=False)

    return JsonResponse({"q": query_param}, safe=False)


def check_user_exists(request):
    # loading the payload body property as a dictionary
    user_data = json.loads(request.body)
    filter_by = user_data.get('filter_by', None)
    # searching the database for the user by username
    user_instance = User.objects.filter(**filter_by).first()

    if user_instance:
        user_dict = user_instance.__dict__
        user_dict.pop('_state')
        user_dict.pop('password')
        return JsonResponse({'exists': True, 'user': user_dict}, safe=True)
    else:
        return JsonResponse({'exists': False})


def check_user_valid(request):
    ldapi = Ldap()
    user = request.GET.get("user")
    user_exists_in_ad = True if ldapi.check_user_exists(user, "mail")[0] is not False else False
    if user_exists_in_ad:
        return JsonResponse(json.dumps({"exists": True}), safe=False)
    else:
        return JsonResponse(json.dumps({
            "exists": False,
            "message": "User does not exist in the organization."
        }), safe=False)


def get_instances(request):
    model_type = request.GET.get("type", None)
    col_filter = request.GET.get("filter", None)
    q = request.GET.get("q", None)
    if model_type is not None and q is not None and col_filter is not None:
        filter_by = {
            f"{col_filter}__icontains": q,
        }
        model = get_objects_by_type(model_type)
        if "_name" in col_filter:
            object_instances = model.objects.filter(**filter_by).values_list("pk", "first_name", "last_name")
            instances_serialized = json.dumps([
                {"id": instance[0], "firstName": instance[1], "lastName": instance[2]}
                for instance in object_instances
            ])
        else:
            object_instances = model.objects.filter(**filter_by).values_list("pk", "name")
            instances_serialized = json.dumps([
                {"id": instance[0], "name": instance[1]}
                for instance in object_instances
            ])
        return JsonResponse(instances_serialized, safe=False)
    else:
        return JsonResponse({"message": "Please provide query parameters"}, safe=False)

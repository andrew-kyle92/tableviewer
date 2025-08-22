from django.contrib.auth.models import User

from tableviewer.models import DynamicTable


def change_member_membership(user, group, change_type, membership, full_remove=False):
    """Add or removes the user to the group with the given membership"""
    try:
        if change_type == "add":
            # add to members group
            group.members.add(user)

            # add to owners group
            if membership == "owner":
                group.owners.add(user)

        elif change_type == "remove":
            # remove from owner's list
            if membership == "owner":
                group.owners.remove(user)
            # remove from member's list
            if membership == "member" or full_remove:
                group.members.remove(user)
    except ValueError as e:
        return e
    except Exception as e:
        return e


def get_objects_by_type(object_type):
    objects = {
        "user": User,
        "table": DynamicTable,
    }
    return objects[object_type]


# ##### User methods #####
def create_user(form):
    """Creates a user in the database and returns the user object"""
    user = User.objects.create_user(
        username=form.cleaned_data['username'],
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'],
        email=form.cleaned_data['email'],
        is_staff=True,
    )
    user.set_unusable_password()
    user.save()

    return user

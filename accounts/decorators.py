from django.template.context_processors import request
from django.shortcuts import redirect

def admin_only(view_func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.groups.exists:
            group=request.user.groups.all()[0].name

            if group == "customer":
                return redirect("store:items")

            if group=="admin":
                return view_func(request,*args,**kwargs)

    return wrapper_func


def authorized_user(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request,*args,**kwargs):
            if request.user.groups.exists:
                group=request.user.groups.all()[0].name

                if group in allowed_roles:
                    return view_func(request,*args,**kwargs)
                else:
                    return redirect("store:items")
        return wrapper_func
    return decorator
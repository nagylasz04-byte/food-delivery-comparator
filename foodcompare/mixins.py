from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Csak bejelentkezett felhasználók láthatják
class LoginRequired(LoginRequiredMixin):
    login_url = "/admin/login/"
    redirect_field_name = None


# Csak az admin (superuser) vagy staff jogosult írni (Create/Update/Delete)
class WritePermissionRequired(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_staff

    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect("/admin/login/")

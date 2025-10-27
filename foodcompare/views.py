from django.views import View
from django.shortcuts import render
from django.urls import get_resolver
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.http import HttpResponse, Http404
from django.conf import settings
from pathlib import Path
from catalog.models import Etterem


class SiteIndexView(View):
    """List available non-parameterized public URL paths for the site root.

    This inspects the project's URL resolver and returns a list of simple
    paths (no path converters like <int:pk>) so the homepage can show links
    to reachable pages during development.
    """
    template_name = "site_index.html"

    def get(self, request):
        # If the visitor is not a staff/admin user, send them straight to the
        # search page instead of showing the site index.
        if not (request.user.is_authenticated and request.user.is_staff):
            return redirect("catalog:kereses")

        resolver = get_resolver()
        patterns = []

        def walk(pattern_list, prefix=""):
            for p in pattern_list:
                try:
                    route = getattr(p, "pattern", None)
                    # convert to string if possible
                    route_str = str(route)
                except Exception:
                    route_str = ""

                # full path candidate
                full = (prefix + route_str).strip()

                # skip admin, static, media and parameterized routes
                if "admin" in full or "static" in full or "media" in full:
                    continue
                if "<" in full or "(" in full or ":" in full:
                    # contains converters or regex groups — skip
                    continue

                # ensure leading slash
                if not full.startswith("/"):
                    full = "/" + full

                # normalize trailing slash
                if not full.endswith("/"):
                    full = full + "/"

                # avoid duplicates
                if full not in patterns:
                    patterns.append(full)

                # recurse into included patterns if present
                if hasattr(p, "url_patterns"):
                    walk(p.url_patterns, prefix=prefix + route_str)

        walk(resolver.url_patterns)

        # sort for deterministic order
        patterns.sort()
        return render(request, self.template_name, {"paths": patterns})


def simple_logout(request):
    """Log out the user and redirect to home. Accepts GET so topbar links work."""
    auth_logout(request)
    return redirect("home")


def scraped_or_redirect(request, etterem_id: int):
    """Serve the local scraped HTML for the restaurant's platform if present.

    If the corresponding file (data/<platform>.html) exists in the project,
    return it as HTML. Otherwise redirect to the restaurant's recorded
    `platform_url` or fallback to `get_platform_url()`.
    """
    try:
        etterem = Etterem.objects.get(pk=etterem_id)
    except Etterem.DoesNotExist:
        raise Http404("Étterem nem található")

    # prefer a scraped HTML file in project_root/data/<platform>.html
    data_dir = Path(settings.BASE_DIR) / "data"
    candidate = data_dir / f"{etterem.platform}.html"
    if candidate.exists():
        return HttpResponse(candidate.read_text(encoding='utf-8'), content_type='text/html')

    # fallback: prefer stored platform_url, otherwise get_platform_url()
    if etterem.platform_url:
        return redirect(etterem.platform_url)
    return redirect(etterem.get_platform_url())

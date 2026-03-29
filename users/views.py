from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from authlib.integrations.django_client import OAuth
from django.conf import settings
from urllib.parse import urlencode
from functools import wraps
import jwt

from predictions.models import UserProfile

APP_CLIENT_ID = "app1-agriculture-client"
APP_REQUIRED_ROLE = "app1_user"


oauth = OAuth()
oauth.register(
    name='keycloak',
    client_id=settings.AUTHLIB_OAUTH_CLIENTS['keycloak']['client_id'],
    client_secret=settings.AUTHLIB_OAUTH_CLIENTS['keycloak']['client_secret'],
    server_metadata_url=settings.AUTHLIB_OAUTH_CLIENTS['keycloak']['server_metadata_url'],
    client_kwargs=settings.AUTHLIB_OAUTH_CLIENTS['keycloak']['client_kwargs'],
)


from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

def has_required_role(access_token, client_id, required_role):
    try:
        decoded = jwt.decode(
            access_token,
            options={"verify_signature": False, "verify_aud": False}
        )
    except Exception:
        return False

    resource_access = decoded.get("resource_access", {})
    client_roles = resource_access.get(client_id, {}).get("roles", [])
    return required_role in client_roles


def require_app_role(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user' not in request.session:
            return redirect('users:login')

        access_token = request.session.get('access_token')
        if not access_token:
            request.session.flush()
            messages.error(request, "Session expired. Please login again.")
            return redirect('users:login')

        if not has_required_role(access_token, APP_CLIENT_ID, APP_REQUIRED_ROLE):
            return redirect('users:unauthorized_access')

        return view_func(request, *args, **kwargs)
    return wrapper


def build_keycloak_logout_url(post_logout_redirect_uri, id_token=None):
    params = {
        "post_logout_redirect_uri": post_logout_redirect_uri,
    }

    if id_token:
        params["id_token_hint"] = id_token

    return f"{settings.KEYCLOAK_LOGOUT_URL}?{urlencode(params)}"


def register(request):
    messages.info(request, "Registration is handled through Keycloak.")
    return redirect('users:login')


@never_cache
def login_view(request):
    if 'user' in request.session:
        return redirect('predictions:home')

    redirect_uri = request.build_absolute_uri('/auth/callback/')
    return oauth.keycloak.authorize_redirect(request, redirect_uri)


@never_cache
def callback_view(request):
    error = request.GET.get("error")
    error_description = request.GET.get("error_description")

    if error:
        if error == "temporarily_unavailable" and error_description == "authentication_expired":
            messages.warning(request, "Login session expired. Please sign in again.")
        else:
            messages.error(request, f"SSO failed: {error_description or error}")
        return redirect('users:login')

    try:
        token = oauth.keycloak.authorize_access_token(request)
    except Exception as e:
        messages.error(request, f"Authentication failed: {str(e)}")
        return redirect('users:login')

    access_token = token.get('access_token')
    if not access_token:
        messages.error(request, "Access token not received from Keycloak.")
        return redirect('users:login')

    if not has_required_role(access_token, APP_CLIENT_ID, APP_REQUIRED_ROLE):
        request.session['id_token'] = token.get('id_token')
        return redirect('users:unauthorized_access')

    userinfo = token.get('userinfo')
    if not userinfo:
        userinfo = oauth.keycloak.userinfo(token=token)

    sub = userinfo.get('sub')
    username = userinfo.get('preferred_username')
    email = userinfo.get('email')
    name = userinfo.get('name')

    request.session['user'] = {
        'sub': sub,
        'username': username,
        'email': email,
        'name': name,
    }
    request.session['id_token'] = token.get('id_token')
    request.session['access_token'] = access_token

    profile, created = UserProfile.objects.get_or_create(
        keycloak_sub=sub,
        defaults={
            'username': username,
            'email': email,
        }
    )

    changed = False
    if not profile.username and username:
        profile.username = username
        changed = True
    if not profile.email and email:
        profile.email = email
        changed = True
    if changed:
        profile.save()

    if not profile.phone or not profile.location or not profile.soil_type or not profile.farm_size:
        return redirect('predictions:complete_profile')

    messages.success(request, f"Welcome, {username}!")
    return redirect('predictions:home')


@never_cache
def logout_view(request):
    id_token = request.session.get('id_token')

    request.session.pop('user', None)
    request.session.pop('id_token', None)
    request.session.pop('access_token', None)
    request.session.flush()

    post_logout_redirect_uri = request.build_absolute_uri('/')

    logout_url = build_keycloak_logout_url(
        post_logout_redirect_uri=post_logout_redirect_uri,
        id_token=id_token
    )
    return redirect(logout_url)


@never_cache
def unauthorized_access(request):
    id_token = request.session.get('id_token')

    request.session.flush()

    post_logout_redirect_uri = request.build_absolute_uri('/auth/login/')

    logout_url = build_keycloak_logout_url(
        post_logout_redirect_uri=post_logout_redirect_uri,
        id_token=id_token
    )
    return redirect(logout_url)


@never_cache
@require_app_role
def profile_view(request):
    profile = UserProfile.objects.filter(
        keycloak_sub=request.session['user'].get('sub')
    ).first()

    return render(request, 'users/profile.html', {
        'user': request.session['user'],
        'profile': profile,
    })
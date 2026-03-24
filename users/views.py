from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from authlib.integrations.django_client import OAuth
from django.conf import settings
from urllib.parse import urlencode

from predictions.models import UserProfile

oauth = OAuth()
oauth.register(
    name='keycloak',
    client_id=settings.AUTHLIB_OAUTH_CLIENTS['keycloak']['client_id'],
    client_secret=settings.AUTHLIB_OAUTH_CLIENTS['keycloak']['client_secret'],
    server_metadata_url=settings.AUTHLIB_OAUTH_CLIENTS['keycloak']['server_metadata_url'],
    client_kwargs=settings.AUTHLIB_OAUTH_CLIENTS['keycloak']['client_kwargs'],
)


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
    token = oauth.keycloak.authorize_access_token(request)
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

    profile, created = UserProfile.objects.get_or_create(
        keycloak_sub=sub,
        defaults={
            'username': username,
            'email': email,
        }
    )

    # Update local profile basics if missing
    changed = False
    if not profile.username and username:
        profile.username = username
        changed = True
    if not profile.email and email:
        profile.email = email
        changed = True
    if changed:
        profile.save()

    # Redirect to complete profile if app-specific fields are missing
    if not profile.phone or not profile.location or not profile.soil_type or not profile.farm_size:
        return redirect('predictions:complete_profile')

    messages.success(request, f"Welcome, {username}!")
    return redirect('predictions:home')


@never_cache
def logout_view(request):
    id_token = request.session.get('id_token')
    request.session.pop('user', None)
    request.session.pop('id_token', None)
    request.session.flush()

    redirect_uri = request.build_absolute_uri('/auth/login/')
    params = {
        "post_logout_redirect_uri": redirect_uri,
        "id_token_hint": id_token,
    }

    logout_url = (
        "http://localhost:8080/realms/sso-demo/protocol/openid-connect/logout?"
        + urlencode(params)
    )
    return redirect(logout_url)


@never_cache
def profile_view(request):
    if 'user' not in request.session:
        return redirect('users:login')

    profile = UserProfile.objects.filter(
        keycloak_sub=request.session['user'].get('sub')
    ).first()

    return render(request, 'users/profile.html', {
        'user': request.session['user'],
        'profile': profile,
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
import pandas as pd
import json

from .forms import CropPredictionForm, CropCSVUploadForm, ProfileCompletionForm
from .ml_model import crop_model
from .models import UserProfile


@never_cache
def home(request):
    if 'user' not in request.session:
        return redirect('users:login')

    profile = UserProfile.objects.filter(
        keycloak_sub=request.session['user'].get('sub')
    ).first()

    if not profile or not profile.phone or not profile.location or not profile.soil_type or not profile.farm_size:
        return redirect('predictions:complete_profile')

    return render(request, 'home.html', {
        'user': request.session.get('user'),
        'profile': profile,
    })


@never_cache
def complete_profile(request):
    if 'user' not in request.session:
        return redirect('users:login')

    sso_user = request.session['user']
    sub = sso_user.get('sub')

    profile, created = UserProfile.objects.get_or_create(
        keycloak_sub=sub,
        defaults={
            'username': sso_user.get('username'),
            'email': sso_user.get('email'),
        }
    )

    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile completed successfully!")
            return redirect('predictions:home')
    else:
        form = ProfileCompletionForm(instance=profile)

    return render(request, 'predictions/complete_profile.html', {
        'form': form,
        'user': sso_user,
    })


@never_cache
@require_http_methods(["GET", "POST"])
def dashboard(request):
    if 'user' not in request.session:
        return redirect('users:login')

    profile = UserProfile.objects.filter(
        keycloak_sub=request.session['user'].get('sub')
    ).first()

    if not profile or not profile.phone or not profile.location or not profile.soil_type or not profile.farm_size:
        return redirect('predictions:complete_profile')

    prediction_form = CropPredictionForm()
    csv_form = CropCSVUploadForm()
    context = {
        'prediction_form': prediction_form,
        'csv_form': csv_form,
        'prediction_result': None,
        'csv_results': None,
        'total_predictions': 0,
        'user': request.session.get('user'),
        'profile': profile,
    }

    if request.method == 'POST':
        if 'single_predict' in request.POST:
            prediction_form = CropPredictionForm(request.POST)
            if prediction_form.is_valid():
                N = prediction_form.cleaned_data['N']
                P = prediction_form.cleaned_data['P']
                K = prediction_form.cleaned_data['K']
                temperature = prediction_form.cleaned_data['temperature']
                humidity = prediction_form.cleaned_data['humidity']
                ph = prediction_form.cleaned_data['ph']
                rainfall = prediction_form.cleaned_data['rainfall']

                result = crop_model.predict_single(N, P, K, temperature, humidity, ph, rainfall)

                if result['success']:
                    context['prediction_result'] = result
                    messages.success(request, f"✓ Predicted Crop: {result['prediction']}")
                else:
                    messages.error(request, f"✗ {result['error']}")
            else:
                messages.error(request, 'Please fill all fields correctly.')

            context['prediction_form'] = prediction_form

        elif 'csv_predict' in request.POST:
            csv_form = CropCSVUploadForm(request.POST, request.FILES)
            if csv_form.is_valid():
                try:
                    csv_file = request.FILES['csv_file']
                    df = pd.read_csv(csv_file)

                    required_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
                    missing_cols = [col for col in required_cols if col not in df.columns]

                    if missing_cols:
                        messages.error(
                            request,
                            f"CSV missing columns: {', '.join(missing_cols)}. Required: {', '.join(required_cols)}"
                        )
                    else:
                        results_df, error = crop_model.predict_batch(df)

                        if error:
                            messages.error(request, f"✗ {error}")
                        else:
                            request.session['prediction_results'] = results_df.to_json(orient='records')
                            context['csv_results'] = results_df.head(10).to_html(
                                classes='table table-striped table-hover',
                                index=False
                            )
                            context['total_predictions'] = len(results_df)
                            messages.success(request, f"✓ Predictions made for {len(results_df)} records!")

                except pd.errors.ParserError:
                    messages.error(request, "✗ Invalid CSV format. Please check the file.")
                except Exception as e:
                    messages.error(request, f"✗ Error reading CSV: {str(e)}")
            else:
                messages.error(request, '✗ Please upload a valid CSV file.')

            context['csv_form'] = csv_form

    return render(request, 'predictions/dashboard.html', context)


@never_cache
def download_results(request):
    if 'user' not in request.session:
        return redirect('users:login')

    results_json = request.session.get('prediction_results')
    if not results_json:
        messages.error(request, '✗ No results to download.')
        return redirect('predictions:dashboard')

    results_data = json.loads(results_json)
    df = pd.DataFrame(results_data)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="crop_predictions.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response


@never_cache
def history(request):
    if 'user' not in request.session:
        return redirect('users:login')

    return render(request, 'predictions/history.html', {
        'message': 'Prediction history feature coming soon!',
        'user': request.session.get('user'),
    })
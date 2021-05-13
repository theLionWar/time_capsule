from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from playlist_creation.forms import PlaylistCreationForm
from playlist_creation.models import Playlist


def home(request):
    if request.method == 'POST':
        form = PlaylistCreationForm(request.POST)
        if form.is_valid():
            playlist: Playlist = form.save()
            request.session['playlist'] = str(playlist.id)
            return HttpResponseRedirect(reverse('social:begin', args=('spotify', )))
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, error)
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = PlaylistCreationForm()
    return render(request, 'home.html', {'form': form})


def thank_you(request):
    return render(request, 'thank_you.html')

from dataclasses import dataclass
from datetime import date

import pylast
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from playlist_creation.models import Playlist, MusicProviders


@dataclass(frozen=True)
class DateWithoutYear:
    day: str
    month: str


def year_choices():
    return [(r, r) for r in range(2005, date.today().year + 1)]


class PlaylistCreationForm(forms.Form):

    SUMMER = 0
    FALL = 1
    WINTER = 2
    SPRING = 3
    SEASONS = [
        (SUMMER, 'Summer'),
        (FALL, 'Fall'),
        (WINTER, 'Winter'),
        (SPRING, 'Spring'),
    ]

    SEASONS_TO_DATES_MAPPING = {
        SUMMER: (DateWithoutYear(1, 6), DateWithoutYear(31, 8)),
        FALL: (DateWithoutYear(1, 9), DateWithoutYear(30, 11)),
        WINTER: (DateWithoutYear(1, 12), DateWithoutYear(28, 2)),
        SPRING: (DateWithoutYear(1, 3), DateWithoutYear(31, 5)),
    }

    season = forms.ChoiceField(label='Pick a season', choices=SEASONS,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.TypedChoiceField(label='Pick a year', coerce=int, choices=year_choices, initial=2012,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    lastfm_username = forms.CharField(label='Last.fm username',
                                      widget=forms.TextInput(attrs={'class': 'form-control',
                                                                    'placeholder': 'Last.fm username'}))

    def clean_lastfm_username(self):
        lastfm_username = self.cleaned_data['lastfm_username']

        lastfm_network = pylast.LastFMNetwork(api_key=settings.LASTFM_API_KEY, api_secret=settings.LASTFM_SHARED_SECRET)
        lastfm_user = pylast.User(user_name=lastfm_username, network=lastfm_network)

        try:
            lastfm_user.get_registered()
        except pylast.PyLastError:
            raise ValidationError("Last.fm user doesn't exist")

        return lastfm_username

    def save(self):
        lastfm_username = self.cleaned_data['lastfm_username']
        season = int(self.cleaned_data['season'])
        year = self.cleaned_data['year']

        from_day = self.SEASONS_TO_DATES_MAPPING[season][0].day
        from_month = self.SEASONS_TO_DATES_MAPPING[season][0].month
        from_date = date(day=from_day, month=from_month, year=year)

        to_day = self.SEASONS_TO_DATES_MAPPING[season][1].day
        to_month = self.SEASONS_TO_DATES_MAPPING[season][1].month
        to_date = date(day=to_day, month=to_month, year=year if season != self.WINTER else year + 1)

        source_providers = {MusicProviders.LASTFM: lastfm_username,
                            MusicProviders.SPOTIFY: None}

        return Playlist.objects.create(source_providers=source_providers, from_date=from_date, to_date=to_date)

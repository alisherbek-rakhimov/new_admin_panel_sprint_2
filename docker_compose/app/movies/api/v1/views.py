from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, Min, Max, Avg, F
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.models import Filmwork
from movies.mixins import RoleType


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        # role = models.TextField(_('role'), choices=self.RoleType.choices, null=True)

        res = Filmwork.objects.values() \
            .annotate(genres=ArrayAgg('genres__name', distinct=True)) \
            .annotate(actors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.ACTOR),
                                      distinct=True)) \
            .annotate(writers=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.WRITER),
                                       distinct=True)) \
            .annotate(directors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.DIRECTOR),
                                         distinct=True)) \
            .order_by('id')

        return res

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()

        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )

        res = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset)
        }
        return res


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        return self.object

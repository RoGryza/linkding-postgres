from django.contrib.auth.models import User
from django.contrib.postgres.aggregates.mixins import OrderableAggMixin
from django.db.models import Q, Count, Value, BooleanField, QuerySet, Aggregate

from bookmarks.models import Bookmark, Tag
from bookmarks.utils import unique


"""Like `django.contrib.postgres.aggregates.StringAgg`, but when empty returns `None` instead of an
empty str.
"""
class StringAgg(OrderableAggMixin, Aggregate):
    function = 'STRING_AGG'
    template = '%(function)s(%(distinct)s%(expressions)s %(ordering)s)'
    allow_distinct = True

    def __init__(self, expression, delimiter, **extra):
        delimiter_expr = Value(str(delimiter))
        super().__init__(expression, delimiter_expr, **extra)


def query_bookmarks(user: User, query_string: str) -> QuerySet:
    return _base_bookmarks_query(user, query_string) \
        .filter(is_archived=False)


def query_archived_bookmarks(user: User, query_string: str) -> QuerySet:
    return _base_bookmarks_query(user, query_string) \
        .filter(is_archived=True)


def _base_bookmarks_query(user: User, query_string: str) -> QuerySet:
    # Add aggregated tag info to bookmark instances
    query_set = Bookmark.objects \
        .annotate(tag_count=Count('tags'),
                  tag_string=StringAgg('tags__name', delimiter=','),
                  tag_projection=Value(True, BooleanField()))

    # Filter for user
    query_set = query_set.filter(owner=user)

    # Split query into search terms and tags
    query = _parse_query_string(query_string)

    # Filter for search terms and tags
    for term in query['search_terms']:
        query_set = query_set.filter(
            Q(title__contains=term)
            | Q(description__contains=term)
            | Q(website_title__contains=term)
            | Q(website_description__contains=term)
            | Q(url__contains=term)
        )

    for tag_name in query['tag_names']:
        query_set = query_set.filter(
            tags__name__iexact=tag_name
        )

    # Untagged bookmarks
    if query['untagged']:
        query_set = query_set.filter(
            tags=None
        )

    # Sort by date added
    query_set = query_set.order_by('-date_added')

    return query_set


def query_bookmark_tags(user: User, query_string: str) -> QuerySet:
    bookmarks_query = query_bookmarks(user, query_string)

    query_set = Tag.objects.filter(bookmark__in=bookmarks_query)

    return query_set.distinct()


def query_archived_bookmark_tags(user: User, query_string: str) -> QuerySet:
    bookmarks_query = query_archived_bookmarks(user, query_string)

    query_set = Tag.objects.filter(bookmark__in=bookmarks_query)

    return query_set.distinct()


def get_user_tags(user: User):
    return Tag.objects.filter(owner=user).all()


def _parse_query_string(query_string):
    # Sanitize query params
    if not query_string:
        query_string = ''

    # Split query into search terms and tags
    keywords = query_string.strip().split(' ')
    keywords = [word for word in keywords if word]

    search_terms = [word for word in keywords if word[0] != '#' and word[0] != '!']
    tag_names = [word[1:] for word in keywords if word[0] == '#']
    tag_names = unique(tag_names, str.lower)

    # Special search commands
    untagged = '!untagged' in keywords

    return {
        'search_terms': search_terms,
        'tag_names': tag_names,
        'untagged': untagged,
    }

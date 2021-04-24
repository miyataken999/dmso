import os
import base64

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from wagtail.search.index import class_is_indexed
from wagtail.search.models import Query
from wagtail.search.backends import get_search_backend

from .types.structures import BasePaginatedType, PaginationType


def resolve_queryset(
    qs,
    info,
    limit=None,
    offset=None,
    search_query=None,
    id=None,
    order=None,
    collection=None,
    **kwargs
):
    """
    Add limit, offset and search capabilities to the query. This contains
    argument names used by
    :class:`~grapple.types.structures.QuerySetList`.
    :param qs: The query set to be modified.
    :param info: The Graphene info object.
    :param limit: Limit number of objects in the QuerySet.
    :type limit: int
    :param id: Filter by the primary key.
    :type id: int
    :param offset: Omit a number of objects from the beginning of the query set
    :type offset: int
    :param search_query: Using Wagtail search, exclude objects that do not match
                         the search query.
    :type search_query: str
    :param order: Order the query set using the Django QuerySet order_by format.
    :type order: str
    :param collection: Use Wagtail's collection id to filter images or documents
    :type collection: int
    """
    offset = int(offset or 0)

    if id is not None:
        qs = qs.filter(pk=id)
    else:
        qs = qs.all()

    if id is None and search_query:
        # Check if the queryset is searchable using Wagtail search.
        if not class_is_indexed(qs.model):
            raise TypeError("This data type is not searchable by Wagtail.")

        if settings.GRAPPLE_ADD_SEARCH_HIT is True:
            query = Query.get(search_query)
            query.add_hit()

        return get_search_backend().search(search_query, qs)

    if order is not None:
        qs = qs.order_by(*map(lambda x: x.strip(), order.split(",")))

    if limit is not None:
        limit = int(limit)
        qs = qs[offset : limit + offset]

    if collection is not None:
        qs = qs.filter(collection=collection)

    return qs


def get_paginated_result(qs, page, per_page):
    """
    Returns a paginated result.
    """
    paginator = Paginator(qs, per_page)

    try:
        # If the page exists and the page is an int
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an int; show the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (too high most likely)
        # Then return the last page
        page_obj = paginator.page(paginator.num_pages)

    return BasePaginatedType(
        items=page_obj.object_list,
        pagination=PaginationType(
            total=paginator.count,
            count=len(page_obj.object_list),
            per_page=per_page,
            current_page=page_obj.number,
            prev_page=page_obj.previous_page_number()
            if page_obj.has_previous()
            else None,
            next_page=page_obj.next_page_number() if page_obj.has_next() else None,
            total_pages=paginator.num_pages,
        ),
    )


def resolve_paginated_queryset(
    qs, info, page=None, per_page=None, search_query=None, id=None, order=None, **kwargs
):
    """
    Add page, per_page and search capabilities to the query. This contains
    argument names used by
    :function:`~grapple.types.structures.PaginatedQuerySet`.
    :param qs: The query set to be modified.
    :param info: The Graphene info object.
    :param page: Page of resulting objects to return from the QuerySet.
    :type page: int
    :param id: Filter by the primary key.
    :type id: int
    :param per_page: The maximum number of items to include on a page.
    :type per_page: int
    :param search_query: Using Wagtail search, exclude objects that do not match
                         the search query.
    :type search_query: str
    :param order: Order the query set using the Django QuerySet order_by format.
    :type order: str
    """
    per_page = int(per_page or 10)

    if id is not None:
        qs = qs.filter(pk=id)
    else:
        qs = qs.all()

    if id is None and search_query:
        # Check if the queryset is searchable using Wagtail search.
        if not class_is_indexed(qs.model):
            raise TypeError("This data type is not searchable by Wagtail.")

        if settings.GRAPPLE_ADD_SEARCH_HIT is True:
            query = Query.get(search_query)
            query.add_hit()

        results = get_search_backend().search(search_query, qs)

        return get_paginated_result(results, page, per_page)

    if order is not None:
        qs = qs.order_by(*map(lambda x: x.strip(), order.split(",")))

    return get_paginated_result(qs, page, per_page)


def get_media_item_url(cls):
    url = ""
    if hasattr(cls, "url"):
        url = cls.url
    elif hasattr(cls, "file"):
        url = cls.file.url

    if url[0] == "/":
        return settings.BASE_URL + url
    return url


def image_as_base64(image_file, format="png"):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    encoded_string = ""
    image_file = settings.BASE_DIR + image_file

    if not os.path.isfile(image_file):
        return "not an image"

    with open(image_file, "rb") as img_f:
        encoded_string = base64.b64encode(img_f.read())

    return "data:image/%s;base64,%s" % (format, encoded_string)

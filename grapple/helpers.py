import graphene
import inspect
from types import MethodType

from django.utils.translation import ugettext_lazy
from wagtail.core.models import Page

from .registry import registry
from .types.streamfield import StreamFieldInterface


streamfield_types = []


def register_streamfield_block(cls):
    base_block = None
    for block_class in inspect.getmro(cls):
        if block_class in registry.streamfield_blocks:
            base_block = registry.streamfield_blocks[block_class]

    streamfield_types.append(
        {
            "cls": cls,
            "type_prefix": "",
            "interface": StreamFieldInterface,
            "base_type": base_block,
        }
    )

    return cls


def register_graphql_schema(schema_cls):
    registry.schema.append(schema_cls)
    return schema_cls


def register_query_field(
    field_name,
    plural_field_name=None,
    query_params=None,
    required=False,
    plural_required=False,
    plural_item_required=False,
):
    from .types.structures import QuerySetList
    from .utils import resolve_queryset

    if not plural_field_name:
        plural_field_name = field_name + "s"

    def inner(cls):
        field_type = lambda: registry.models[cls]
        field_query_params = query_params
        if field_query_params is None:
            field_query_params = {"id": graphene.Int()}

            if issubclass(cls, Page):
                field_query_params["slug"] = graphene.Argument(
                    graphene.String, description=ugettext_lazy("The page slug.")
                )
                field_query_params["url_path"] = graphene.Argument(
                    graphene.String, description=ugettext_lazy("The url path.")
                )
                field_query_params["token"] = graphene.Argument(
                    graphene.String, description=ugettext_lazy("The preview token.")
                )

        def Mixin():
            # Generic methods to get all and query one model instance.
            def resolve_singular(self, _, info, **kwargs):
                # If no filters then return nothing,
                if not kwargs:
                    return None

                try:
                    # If is a Page then only query live/public pages.
                    if issubclass(cls, Page):
                        if "token" in kwargs and hasattr(
                            cls, "get_page_from_preview_token"
                        ):
                            return cls.get_page_from_preview_token(kwargs["token"])

                        qs = cls.objects.live().public()
                        url_path = kwargs.pop("url_path", None)
                        if url_path:
                            if not url_path.endswith("/"):
                                url_path += "/"
                            return qs.filter(
                                url_path__endswith=url_path, **kwargs
                            ).first()

                        return qs.get(**kwargs)

                    return cls.objects.get(**kwargs)
                except Exception as e:
                    return None

            def resolve_plural(self, _, info, **kwargs):
                qs = cls.objects
                if issubclass(cls, Page):
                    qs = qs.live().public().order_by("-first_published_at")

                return resolve_queryset(qs.all(), info, **kwargs)

            # Create schema and add resolve methods
            schema = type(cls.__name__ + "Query", (), {})

            singular_field_type = field_type
            if required:
                singular_field_type = graphene.NonNull(field_type)

            setattr(
                schema,
                field_name,
                graphene.Field(singular_field_type, **field_query_params),
            )

            plural_field_type = field_type
            if plural_item_required:
                plural_field_type = graphene.NonNull(field_type)

            setattr(
                schema,
                plural_field_name,
                QuerySetList(plural_field_type, required=plural_required),
            )

            setattr(
                schema, "resolve_" + field_name, MethodType(resolve_singular, schema)
            )
            setattr(
                schema,
                "resolve_" + plural_field_name,
                MethodType(resolve_plural, schema),
            )
            return schema

        # Send schema to Grapple schema.
        register_graphql_schema(Mixin())
        return cls

    return inner


def register_paginated_query_field(
    field_name,
    plural_field_name=None,
    query_params=None,
    required=False,
    plural_required=False,
    plural_item_required=False,
):
    from .types.structures import PaginatedQuerySet
    from .utils import resolve_paginated_queryset

    if not plural_field_name:
        plural_field_name = field_name + "s"

    def inner(cls):
        field_type = lambda: registry.models[cls]
        field_query_params = query_params
        if field_query_params is None:
            field_query_params = {"id": graphene.Int()}

            if issubclass(cls, Page):
                field_query_params["slug"] = graphene.Argument(
                    graphene.String, description=ugettext_lazy("The page slug.")
                )
                field_query_params["url_path"] = graphene.Argument(
                    graphene.String, description=ugettext_lazy("The page url path.")
                )
                field_query_params["token"] = graphene.Argument(
                    graphene.String, description=ugettext_lazy("The preview token.")
                )

        def Mixin():
            # Generic methods to get all and query one model instance.
            def resolve_singular(self, _, info, **kwargs):
                # If no filters then return nothing.
                if not kwargs:
                    return None

                try:
                    # If is a Page then only query live/public pages.
                    if issubclass(cls, Page):
                        if "token" in kwargs and hasattr(
                            cls, "get_page_from_preview_token"
                        ):
                            return cls.get_page_from_preview_token(kwargs["token"])

                        qs = cls.objects.live().public()
                        url_path = kwargs.pop("url_path", None)
                        if url_path:
                            if not url_path.endswith("/"):
                                url_path += "/"
                            return qs.filter(
                                url_path__endswith=url_path, **kwargs
                            ).first()
                        return qs.get(**kwargs)

                    return cls.objects.get(**kwargs)
                except:
                    return None

            def resolve_plural(self, _, info, **kwargs):
                qs = cls.objects
                if issubclass(cls, Page):
                    qs = qs.live().public().order_by("-first_published_at")

                return resolve_paginated_queryset(qs.all(), info, **kwargs)

            # Create schema and add resolve methods
            schema = type(cls.__name__ + "Query", (), {})

            singular_field_type = field_type
            if required:
                singular_field_type = graphene.NonNull(field_type)

            setattr(
                schema,
                field_name,
                graphene.Field(singular_field_type, **field_query_params),
            )

            plural_field_type = field_type
            if plural_item_required:
                plural_field_type = graphene.NonNull(field_type)

            setattr(
                schema,
                plural_field_name,
                PaginatedQuerySet(plural_field_type, cls, required=plural_required),
            )

            setattr(
                schema, "resolve_" + field_name, MethodType(resolve_singular, schema)
            )
            setattr(
                schema,
                "resolve_" + plural_field_name,
                MethodType(resolve_plural, schema),
            )
            return schema

        # Send schema to Grapple schema.
        register_graphql_schema(Mixin())
        return cls

    return inner


def register_singular_query_field(field_name, query_params=None, required=False):
    def inner(cls):
        field_type = lambda: registry.models[cls]
        field_query_params = query_params

        if field_query_params is None:
            field_query_params = {
                "order": graphene.Argument(
                    graphene.String,
                    description=ugettext_lazy(
                        "Use the Django QuerySet order_by format."
                    ),
                ),
            }
            if issubclass(cls, Page):
                field_query_params["token"] = graphene.Argument(
                    graphene.String, description=ugettext_lazy("The preview token.")
                )

        def Mixin():
            # Generic methods to get all and query one model instance.
            def resolve_singular(self, _, info, **kwargs):
                try:
                    qs = cls.objects
                    if "order" in kwargs:
                        qs = qs.order_by(kwargs.pop("order"))

                    # If is a Page then only query live/public pages.
                    if issubclass(cls, Page):
                        if "token" in kwargs and hasattr(
                            cls, "get_page_from_preview_token"
                        ):
                            return cls.get_page_from_preview_token(kwargs["token"])

                        return qs.live().public().filter(**kwargs).first()

                    return qs.filter(**kwargs).first()
                except:
                    return None

            # Create schema and add resolve methods
            schema = type(cls.__name__ + "Query", (), {})

            singular_field_type = field_type
            if required:
                singular_field_type = graphene.NonNull(field_type)

            setattr(
                schema,
                field_name,
                graphene.Field(singular_field_type, **field_query_params),
            )

            setattr(
                schema, "resolve_" + field_name, MethodType(resolve_singular, schema)
            )
            return schema

        # Send schema to Grapple schema.
        register_graphql_schema(Mixin())
        return cls

    return inner

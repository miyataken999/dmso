import graphene
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from wagtail.core.models import Page as WagtailPage, Site
from wagtail_headless_preview.signals import preview_update
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLLocatedError

try:
    from channels.routing import route_class

    has_channels = True
except ImportError:
    has_channels = False

from ..registry import registry
from ..utils import resolve_queryset
from .structures import QuerySetList


class PageInterface(graphene.Interface):
    id = graphene.ID()
    title = graphene.String(required=True)
    slug = graphene.String(required=True)
    content_type = graphene.String(required=True)
    page_type = graphene.String()
    live = graphene.Boolean(required=True)

    url = graphene.String()
    url_path = graphene.String(required=True)

    depth = graphene.Int()
    seo_title = graphene.String(required=True)
    search_description = graphene.String()
    show_in_menus = graphene.Boolean(required=True)

    locked = graphene.Boolean()

    first_published_at = graphene.DateTime()
    last_published_at = graphene.DateTime()

    parent = graphene.Field(lambda: PageInterface)
    children = QuerySetList(
        graphene.NonNull(lambda: PageInterface), enable_search=True, required=True
    )
    siblings = QuerySetList(
        graphene.NonNull(lambda: PageInterface), enable_search=True, required=True
    )
    next_siblings = QuerySetList(
        graphene.NonNull(lambda: PageInterface), enable_search=True, required=True
    )
    previous_siblings = QuerySetList(
        graphene.NonNull(lambda: PageInterface), enable_search=True, required=True
    )
    descendants = QuerySetList(
        graphene.NonNull(lambda: PageInterface), enable_search=True, required=True
    )
    ancestors = QuerySetList(
        graphene.NonNull(lambda: PageInterface), enable_search=True, required=True
    )

    @classmethod
    def resolve_type(cls, instance, info, **kwargs):
        """
        If model has a custom Graphene Node type in registry then use it,
        otherwise use base page type.
        """
        return registry.pages.get(type(instance), Page)

    def resolve_content_type(self, info, **kwargs):
        self.content_type = ContentType.objects.get_for_model(self)
        return (
            self.content_type.app_label + "." + self.content_type.model_class().__name__
        )

    def resolve_page_type(self, info, **kwargs):
        return PageInterface.resolve_type(self.specific, info, **kwargs)

    def resolve_parent(self, info, **kwargs):
        """
        Resolves the parent node of current page node.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/model_reference.html#wagtail.core.models.Page.get_parent
        """
        try:
            return self.get_parent().specific
        except GraphQLLocatedError:
            return WagtailPage.objects.none()

    def resolve_children(self, info, **kwargs):
        """
        Resolves a list of live children of this page.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/queryset_reference.html#examples
        """
        return resolve_queryset(
            self.get_children().live().public().specific(), info, **kwargs
        )

    def resolve_siblings(self, info, **kwargs):
        """
        Resolves a list of sibling nodes to this page.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/queryset_reference.html?highlight=get_siblings#wagtail.core.query.PageQuerySet.sibling_of
        """
        return resolve_queryset(
            self.get_siblings().exclude(pk=self.pk).live().public().specific(),
            info,
            **kwargs,
        )

    def resolve_next_siblings(self, info, **kwargs):
        """
        Resolves a list of direct next siblings of this page. Similar to `resolve_siblings` with sorting.
        Source: https://github.com/wagtail/wagtail/blob/master/wagtail/core/models.py#L1384
        """
        return resolve_queryset(
            self.get_next_siblings().exclude(pk=self.pk).live().public().specific(),
            info,
            **kwargs,
        )

    def resolve_previous_siblings(self, info, **kwargs):
        """
        Resolves a list of direct prev siblings of this page. Similar to `resolve_siblings` with sorting.
        Source: https://github.com/wagtail/wagtail/blob/master/wagtail/core/models.py#L1387
        """
        return resolve_queryset(
            self.get_prev_siblings().exclude(pk=self.pk).live().public().specific(),
            info,
            **kwargs,
        )

    def resolve_descendants(self, info, **kwargs):
        """
        Resolves a list of nodes pointing to the current page’s descendants.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/model_reference.html#wagtail.core.models.Page.get_descendants
        """
        return resolve_queryset(
            self.get_descendants().live().public().specific(), info, **kwargs
        )

    def resolve_ancestors(self, info, **kwargs):
        """
        Resolves a list of nodes pointing to the current page’s ancestors.
        Docs: https://docs.wagtail.io/en/stable/reference/pages/model_reference.html#wagtail.core.models.Page.get_ancestors
        """
        return resolve_queryset(
            self.get_ancestors().live().public().specific(), info, **kwargs
        )

    def resolve_seo_title(self, info, **kwargs):
        """
        Get page's SEO title. Fallback to a normal page's title if absent.
        """
        return self.seo_title or self.title


class Page(DjangoObjectType):
    """
    Base Page type used if one isn't generated for the current model.
    All other node types extend this.
    """

    class Meta:
        model = WagtailPage
        interfaces = (PageInterface,)


def get_specific_page(
    id=None, slug=None, url_path=None, token=None, content_type=None, site=None
):
    """
    Get a specific page, given a page_id, slug or preview if a preview token is passed
    """
    page = None
    try:
        # Everything but the special RootPage
        qs = WagtailPage.objects.live().public().filter(depth__gt=1).specific()
        ctype = None
        if site:
            qs = qs.in_site(site)

        if content_type:
            app_label, model = content_type.lower().split(".")
            ctype = ContentType.objects.get(app_label=app_label, model=model)
            qs = qs.filter(content_type=ctype)

        if id:
            page = qs.get(pk=id)
        elif slug:
            page = qs.get(slug=slug)
        elif url_path:
            if not url_path.endswith("/"):
                url_path += "/"

            if site:
                # Got a site, so make the url_path query as specific as possible
                qs = qs.filter(
                    url_path=f"{site.root_page.url_path}{url_path.lstrip('/')}"
                )
            else:
                # if the url_path is not specific enough, or the same url_path exists under multiple
                # site roots, only the first one will be returned.
                # To-Do: make site a 1st class argument on the page query, rather than just `in_site`
                qs = qs.filter(url_path__endswith=url_path)

            if qs.exists():
                page = qs.first()

        # If token provided then get draft/preview
        if token:
            if page:
                page_type = type(page)
                if hasattr(page_type, "get_page_from_preview_token"):
                    page = page_type.get_page_from_preview_token(token)

            elif ctype:
                cls = ctype.model_class()
                if hasattr(cls, "get_page_from_preview_token"):
                    page = cls.get_page_from_preview_token(token)
    except BaseException:
        page = None

    return page


def PagesQuery():
    # Add base type to registry
    registry.pages[type(WagtailPage)] = Page

    class Mixin:
        pages = QuerySetList(
            graphene.NonNull(lambda: PageInterface),
            content_type=graphene.Argument(
                graphene.String,
                description=_("Filter by content type. Uses the `app.Model` notation."),
            ),
            in_site=graphene.Argument(
                graphene.Boolean,
                description=_("Filter to pages in the current site only."),
                default_value=False,
            ),
            enable_search=True,
            required=True,
        )
        page = graphene.Field(
            PageInterface,
            id=graphene.Int(),
            slug=graphene.String(),
            url_path=graphene.Argument(
                graphene.String,
                description=_(
                    "Filter by url path. Note: in a multi-site setup, returns the first available page based. "
                    "Use `inSite: true` from the relevant site domain."
                ),
            ),
            token=graphene.Argument(
                graphene.String,
                description=_(
                    "Filter by preview token as passed by the `wagtail-headless-preview` package."
                ),
            ),
            content_type=graphene.Argument(
                graphene.String,
                description=_(
                    "Filter by content type using the app.ModelName notation. e.g. `myapp.BlogPage`"
                ),
            ),
            in_site=graphene.Argument(
                graphene.Boolean,
                description=_("Filter to pages in the current site only."),
                default_value=False,
            ),
        )

        # Return all pages in site, ideally specific.
        def resolve_pages(self, info, **kwargs):
            pages = (
                WagtailPage.objects.live().public().filter(depth__gt=1).specific()
            )  # no need to the root page

            if kwargs.get("in_site", False):
                site = Site.find_for_request(info.context)
                pages = pages.in_site(site)

            content_type = kwargs.pop("content_type", None)
            if content_type:
                app_label, model = content_type.strip().lower().split(".")
                try:
                    ctype = ContentType.objects.get(app_label=app_label, model=model)
                except:  # noqa
                    return (
                        WagtailPage.objects.none()
                    )  # something not quite right here, bail out early
                else:
                    pages = pages.filter(content_type=ctype)

            return resolve_queryset(pages, info, **kwargs)

        # Return a specific page, identified by ID or Slug.
        def resolve_page(self, info, **kwargs):
            return get_specific_page(
                id=kwargs.get("id"),
                slug=kwargs.get("slug"),
                url_path=kwargs.get("url_path"),
                token=kwargs.get("token"),
                content_type=kwargs.get("content_type"),
                site=Site.find_for_request(info.context)
                if kwargs.get("in_site", False)
                else None,
            )

    return Mixin


if has_channels:
    from rx.subjects import Subject

    # Subject to sync Django Signals to Observable
    preview_subject = Subject()

    @receiver(preview_update)
    def on_updated(sender, token, **kwargs):
        preview_subject.on_next(token)

    # Subscription Mixin
    def PagesSubscription():
        def preview_observable(id, slug, url_path, token, content_type, site):
            return preview_subject.filter(
                lambda previewToken: previewToken == token
            ).map(
                lambda token: get_specific_page(
                    id, slug, url_path, token, content_type, site
                )
            )

        class Mixin:
            page = graphene.Field(
                PageInterface,
                id=graphene.Int(),
                slug=graphene.String(),
                url_path=graphene.Argument(
                    graphene.String,
                    description=_(
                        "Filter by url path. Note: in a multi-site setup, returns the first available page based. "
                        "Use `inSite: true` from the relevant site domain."
                    ),
                ),
                token=graphene.Argument(
                    graphene.String,
                    description=_(
                        "Filter by preview token as passed by the `wagtail-headless-preview` package."
                    ),
                ),
                content_type=graphene.Argument(
                    graphene.String,
                    description=_(
                        "Filter by content type using the `app.ModelName` notation. e.g. `myapp.BlogPage`"
                    ),
                ),
                in_site=graphene.Argument(
                    graphene.Boolean,
                    description=_("Filter to pages in the current site only."),
                    default_value=False,
                ),
            )

            def resolve_page(self, info, **kwargs):
                return preview_observable(
                    id=kwargs.get("id"),
                    slug=kwargs.get("slug"),
                    url_path=kwargs.get("url_path"),
                    token=kwargs.get("token"),
                    content_type=kwargs.get("content_type"),
                    site=Site.find_for_request(info.context)
                    if kwargs.get("in_site", False)
                    else None,
                )

        return Mixin

import graphene
import wagtail
import inspect
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.snippets.blocks
from django.conf import settings
from django.template.loader import render_to_string
from graphene.types import Scalar
from graphene_django.converter import convert_django_field
from wagtail.core.fields import StreamField
from wagtail.core.rich_text import expand_db_html
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedValue
from wagtail.embeds.embeds import get_embed
from wagtail.embeds.exceptions import EmbedException

from ..registry import registry


class GenericStreamFieldInterface(Scalar):
    @staticmethod
    def serialize(stream_value):
        return stream_value.stream_data


@convert_django_field.register(StreamField)
def convert_stream_field(field, registry=None):
    return GenericStreamFieldInterface(
        description=field.help_text, required=not field.null
    )


class StreamFieldInterface(graphene.Interface):
    id = graphene.String()
    block_type = graphene.String(required=True)
    field = graphene.String(required=True)
    raw_value = graphene.String(required=True)

    @classmethod
    def resolve_type(cls, instance, info):
        """
        If block has a custom Graphene Node type in registry then use it,
        otherwise use generic block type.
        """
        if hasattr(instance, "block"):
            mdl = type(instance.block)
            if mdl in registry.streamfield_blocks:
                return registry.streamfield_blocks[mdl]

            for block_class in inspect.getmro(mdl):
                if block_class in registry.streamfield_blocks:
                    return registry.streamfield_blocks[block_class]

        return registry.streamfield_blocks["generic-block"]

    def resolve_id(self, info, **kwargs):
        return self.id

    def resolve_block_type(self, info, **kwargs):
        return type(self.block).__name__

    def resolve_field(self, info, **kwargs):
        return self.block.name

    def resolve_raw_value(self, info, **kwargs):
        if isinstance(self, blocks.StructValue):
            # This is the value for a nested StructBlock defined via GraphQLStreamfield
            return serialize_struct_obj(self)
        if isinstance(self.value, dict):
            return serialize_struct_obj(self.value)

        return self.value


def generate_streamfield_union(graphql_types):
    class StreamfieldUnion(graphene.Union):
        class Meta:
            types = graphql_types

        @classmethod
        def resolve_type(cls, instance, info):
            """
            If block has a custom Graphene Node type in registry then use it,
            otherwise use generic block type.
            """
            mdl = type(instance.block)
            if mdl in registry.streamfield_blocks:
                return registry.streamfield_blocks[mdl]

            return registry.streamfield_blocks["generic-block"]

    return StreamfieldUnion


class StructBlockItem:
    id = None
    block = None
    value = None

    def __init__(self, id, block, value=""):
        self.id = id
        self.block = block
        self.value = value


def serialize_struct_obj(obj):
    rtn_obj = {}

    if hasattr(obj, "stream_data"):
        rtn_obj = []
        for field in obj.stream_data:
            rtn_obj.append(serialize_struct_obj(field["value"]))
    else:
        for field in obj:
            value = obj[field]
            if hasattr(value, "stream_data"):
                rtn_obj[field] = list(
                    map(
                        lambda data: serialize_struct_obj(data["value"]),
                        value.stream_data,
                    )
                )
            elif hasattr(value, "value"):
                rtn_obj[field] = value.value
            elif hasattr(value, "src"):
                rtn_obj[field] = value.src
            elif hasattr(value, "file"):
                rtn_obj[field] = value.file.url
            else:
                rtn_obj[field] = value

    return rtn_obj


class StructBlock(graphene.ObjectType):
    class Meta:
        interfaces = (StreamFieldInterface,)

    blocks = graphene.List(graphene.NonNull(StreamFieldInterface), required=True)

    def resolve_blocks(self, info, **kwargs):
        stream_blocks = []

        if issubclass(type(self.value), wagtail.core.blocks.stream_block.StreamValue):
            # self: StreamChild, block: StreamBlock, value: StreamValue
            stream_data = self.value.stream_data
            child_blocks = self.value.stream_block.child_blocks
        else:
            # This occurs when StreamBlock is child of StructBlock
            # self: StructBlockItem, block: StreamBlock, value: list
            stream_data = self.value
            child_blocks = self.block.child_blocks

        for field, value in stream_data.items():
            block = dict(child_blocks)[field]
            if issubclass(
                type(block), wagtail.core.blocks.ChooserBlock
            ) or not issubclass(type(block), blocks.StructBlock):
                if isinstance(value, int):
                    value = block.to_python(value)

            stream_blocks.append(StructBlockItem(field, block, value))

        return stream_blocks


class StreamBlock(StructBlock):
    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_blocks(self, info, **kwargs):
        stream_blocks = []
        for stream in self.value.stream_data:
            if type(stream) == tuple:
                # As of Wagtail 2.11 stream_data is a list of dicts (when lazy) or tuples
                # when not lazy. The tuple is (block_type, value, id) where value has been run through bulk_to_python()
                # @see https://github.com/wagtail/wagtail/pull/5976
                block_type, value, _ = stream
                block = self.value.stream_block.child_blocks[block_type]
            else:
                block_type = stream["type"]
                value = stream["value"]
                block = self.value.stream_block.child_blocks[block_type]
                if issubclass(
                    type(block), wagtail.core.blocks.ChooserBlock
                ) or not issubclass(type(block), blocks.StructBlock):
                    value = block.to_python(value)

            stream_blocks.append(StructBlockItem(block_type, block, value))
        return stream_blocks


class StreamFieldBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class CharBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class TextBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class EmailBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class IntegerBlock(graphene.ObjectType):
    value = graphene.Int(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class FloatBlock(graphene.ObjectType):
    value = graphene.Float(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class DecimalBlock(graphene.ObjectType):
    value = graphene.Float(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class RegexBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class URLBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class BooleanBlock(graphene.ObjectType):
    value = graphene.Boolean(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class DateBlock(graphene.ObjectType):
    value = graphene.String(format=graphene.String(), required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_value(self, info, **kwargs):
        format = kwargs.get("format")
        if format:
            return self.value.strftime(format)
        return self.value


class DateTimeBlock(DateBlock):
    class Meta:
        interfaces = (StreamFieldInterface,)


class TimeBlock(DateBlock):
    class Meta:
        interfaces = (StreamFieldInterface,)


class RichTextBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_value(self, info, **kwargs):
        # Allow custom markup for RichText
        return render_to_string(
            "wagtailcore/richtext.html", {"html": expand_db_html(self.value.source)}
        )


class RawHTMLBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class BlockQuoteBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class ChoiceOption(graphene.ObjectType):
    key = graphene.String(required=True)
    value = graphene.String(required=True)


class ChoiceBlock(graphene.ObjectType):
    value = graphene.String(required=True)
    choices = graphene.List(graphene.NonNull(ChoiceOption), required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_choices(self, info, **kwargs):
        choices = []
        for key, value in self.block._constructor_kwargs["choices"]:
            choice = ChoiceOption(key, value)
            choices.append(choice)
        return choices


def get_media_url(url):
    if url[0] == "/":
        return settings.BASE_URL + url
    return url


def get_embed_url(instance):
    return instance.value.url if hasattr(instance, "value") else instance.url


def get_embed_object(instance):
    try:
        return get_embed(get_embed_url(instance))
    except EmbedException:
        pass


class EmbedBlock(graphene.ObjectType):
    value = graphene.String(required=True)
    url = graphene.String(required=True)
    embed = graphene.String()
    raw_embed = graphene.JSONString()

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_url(self, info, **kwargs):
        return get_media_url(get_embed_url(self))

    def resolve_raw_value(self, info, **kwargs):
        if isinstance(self, EmbedValue):
            return self
        return StreamFieldInterface.resolve_raw_value(info, **kwargs)

    def resolve_embed(self, info, **kwargs):
        embed = get_embed_object(self)
        if embed:
            return embed.html

    def resolve_raw_embed(self, info, **kwargs):
        embed = get_embed_object(self)
        if embed:
            return {
                "title": embed.title,
                "type": embed.type,
                "thumbnail_url": embed.thumbnail_url,
                "width": embed.width,
                "height": embed.height,
                "html": embed.html,
            }


class StaticBlock(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)


class ListBlock(graphene.ObjectType):
    items = graphene.List(graphene.NonNull(StreamFieldInterface), required=True)

    class Meta:
        interfaces = (StreamFieldInterface,)

    def resolve_items(self, info, **kwargs):
        # Get the nested StreamBlock type
        block_type = self.block.child_block
        # Return a list of GraphQL types from the list of values
        return [StructBlockItem(self.id, block_type, item) for item in self.value]


registry.streamfield_blocks.update(
    {
        "generic-block": StreamFieldBlock,
        blocks.CharBlock: CharBlock,
        blocks.TextBlock: TextBlock,
        blocks.EmailBlock: EmailBlock,
        blocks.IntegerBlock: IntegerBlock,
        blocks.FloatBlock: FloatBlock,
        blocks.DecimalBlock: DecimalBlock,
        blocks.RegexBlock: RegexBlock,
        blocks.URLBlock: URLBlock,
        blocks.BooleanBlock: BooleanBlock,
        blocks.DateBlock: DateBlock,
        blocks.TimeBlock: TimeBlock,
        blocks.DateTimeBlock: DateTimeBlock,
        blocks.RichTextBlock: RichTextBlock,
        blocks.RawHTMLBlock: RawHTMLBlock,
        blocks.BlockQuoteBlock: BlockQuoteBlock,
        blocks.ChoiceBlock: ChoiceBlock,
        blocks.StreamBlock: StreamBlock,
        blocks.StructBlock: StructBlock,
        blocks.StaticBlock: StaticBlock,
        blocks.ListBlock: ListBlock,
        wagtail.embeds.blocks.EmbedBlock: EmbedBlock,
    }
)


def register_streamfield_blocks():
    from .pages import PageInterface
    from .documents import get_document_type
    from .images import get_image_type

    class PageChooserBlock(graphene.ObjectType):
        page = graphene.Field(PageInterface, required=True)

        class Meta:
            interfaces = (StreamFieldInterface,)

        def resolve_page(self, info, **kwargs):
            return self.value.specific

    class DocumentChooserBlock(graphene.ObjectType):
        document = graphene.Field(get_document_type(), required=True)

        class Meta:
            interfaces = (StreamFieldInterface,)

        def resolve_document(self, info, **kwargs):
            return self.value

    class ImageChooserBlock(graphene.ObjectType):
        image = graphene.Field(get_image_type(), required=True)

        class Meta:
            interfaces = (StreamFieldInterface,)

        def resolve_image(self, info, **kwargs):
            return self.value

    class SnippetChooserBlock(graphene.ObjectType):
        snippet = graphene.String(required=True)

        class Meta:
            interfaces = (StreamFieldInterface,)

        def resolve_snippet(self, info, **kwargs):
            return self.value

    registry.streamfield_blocks.update(
        {
            blocks.PageChooserBlock: PageChooserBlock,
            wagtail.documents.blocks.DocumentChooserBlock: DocumentChooserBlock,
            wagtail.images.blocks.ImageChooserBlock: ImageChooserBlock,
            wagtail.snippets.blocks.SnippetChooserBlock: SnippetChooserBlock,
        }
    )

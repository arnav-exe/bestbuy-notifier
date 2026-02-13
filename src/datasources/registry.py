# for registering all data sources
class SourceRegistry():
    sources: dict = {}  # store all instantiated source objs

    @classmethod
    def register(cls, source_cls):
        """
        cls.sources = 'sources' dict inside SourceRegistry class
        "source_cls.source_name" = name of key for 'sources' dict
        'source_cls' = source class obj reference which is the item of the dict
        """
        cls.sources[source_cls.source_name] = source_cls

    @classmethod
    def get(cls, source_name):
        return cls.sources[source_name]

    @classmethod
    def all(cls) -> dict:  # return dict with all registered data source objs
        return cls.sources

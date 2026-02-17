# for registering all data sources
import logging

class SourceRegistry():
    sources: dict = {}  # store all instantiated source objs
    logger: logging.Logger = None

    @classmethod
    def set_logger(cls, logger: logging.Logger):
        cls.logger = logger

    @classmethod
    def register(cls, source_cls):
        if cls.logger:  # if logger is NOT None
            source_logger = cls.logger.getChild(source_cls.source_name)
        else:
            source_logger = None

        """
        cls.sources = 'sources' dict inside SourceRegistry class
        "source_cls.source_name" = name of key for 'sources' dict
        'inst' = INSTANTIATED source class which is the item of the dict with logger
        """
        cls.sources[source_cls.source_name] = source_cls(logger=source_logger)

    @classmethod
    def get(cls, source_name):
        return cls.sources[source_name]

    @classmethod
    def all(cls) -> dict:  # return dict with all registered data source objs
        return cls.sources

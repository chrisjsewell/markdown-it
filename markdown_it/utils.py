class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

        # recursively apply to all nested dictionaries
        for key, item in list(self.items()):
            if isinstance(item, dict):
                self[key] = AttrDict(item)

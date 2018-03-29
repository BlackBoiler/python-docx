from ..shared import ElementProxy, Emu

class Comments(ElementProxy):

    __slots__=()

    def __contains__(self,id):
        """Enables 'in' operator on comment id"""
        raise NotImplemented

    def __getitem__(self,id):
        """Enables access to comment by id"""
        raise NotImplemented

    def __iter__(self):
        raise NotImplemented

    def __len__(self):
        raise NotImplemented

    def add_comment(self,id,text):
        raise NotImplemented
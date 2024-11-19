from abc import ABC, abstractmethod


class RecursivelyBindableBase(ABC):
    @abstractmethod
    def get_unbound_items(self):
        """
        Yield the contained items which need to be bound before self can be
        bound. Each contained item should either be an unbound method or
        another RecursivelyBindableBase subclass instance.
        """

    @abstractmethod
    def get_bound(self, bound_items):
        """
        Assume that bound_items are bound versions of the items yielded by
        .get_unbound_items(), and return the result of binding self to the
        object that bound_items are bound to.
        """

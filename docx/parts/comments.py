# encoding: utf-8

"""
Provides CommentsPart and related objects
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os

from ..opc.constants import CONTENT_TYPE as CT
from ..opc.packuri import PackURI
from ..opc.part import XmlPart
from ..oxml import parse_xml
from ..comments.comments import Comments


class CommentsPart(XmlPart):
    """
        Proxy for the styles.xml part containing style definitions for a document
        or glossary.
        """

    @classmethod
    def default(cls, package):
        """
        Return a newly created styles part, containing a default set of
        elements.
        """
        partname = PackURI('/word/comments.xml')
        content_type = CT.WML_COMMENTS
        element = parse_xml(cls._default_comments_xml())
        return cls(partname, content_type, element, package)

    @property
    def comments(self):
        """
        The |_Comments| instance containing the styles (<w:comment> element
        proxies) for this styles part.
        """
        return Comments(self.element)

    @classmethod
    def _default_comments_xml(cls):
        """
        Return a bytestream containing XML for a default comments part.
        """
        path = os.path.join(
            os.path.split(__file__)[0], '..', 'templates',
            'default-comments.xml'
        )
        with open(path, 'rb') as f:
            xml_bytes = f.read()
        return xml_bytes

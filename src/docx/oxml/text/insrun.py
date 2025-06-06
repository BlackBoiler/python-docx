from docx.oxml.ns import qn
from docx.oxml.parser import OxmlElement
from docx.oxml.xmlchemy import (
    BaseOxmlElement, OptionalAttribute, ZeroOrMore, ZeroOrOne
)


class CT_IR(BaseOxmlElement):
    """
    ``<w:ins>`` element, containing the properties and text for a insert run.
    """
    r = ZeroOrMore('w:r')

    def add_t(self,text):
        """
        Return a newly added ''<w:t>'' element containing *text*.
        """
        self._r=self._add_r(text=text)

        if len(text.strip()) < len(text):
            self._r.set(qn('xml:space'), 'preserve')
        return self._r

    @property
    def text(self):
        """
        A string representing the textual content of this run, with content
        child elements like ``<w:tab/>`` translated to their Python
        equivalent.
        """
        text = ''
        for child in self:
            if child.tag == qn('w:r'):
                text += child.text
        return text

    @text.setter
    def text(self, text):
        self.clear_content()
        new_run = OxmlElement("w:r")
        new_run.text = text
        self.append(new_run)

    def copy_rpr(self,rprCopy):
        rPr = self._r.get_or_add_rPr()
        for p in rprCopy[:]:
            rPr.append(p)

    @property
    def rpr(self):
        return self._r.rPr

    @rpr.setter
    def rpr(self, value):
        self.copy_rpr(value)

    @property
    def style(self):
        """
        String contained in w:val attribute of <w:rStyle> grandchild, or
        |None| if that element is not present.
        """
        rPr = self._r.rPr
        if rPr is None:
            return None
        return rPr.style

    @style.setter
    def style(self, style):
        """
        Set the character style of this <w:r> element to *style*. If *style*
        is None, remove the style element.
        """
        rPr = self._r.get_or_add_rPr()
        rPr.style = style

    def clear_content(self):
        """
        Remove all child elements except the ``<w:rPr>`` element if present.
        """
        # content_child_elms = self[1:] if self.rPr is not None else self[:]
        for child in self[:]:
            self.remove(child)




class _RunContentAppender(object):
    """
    Service object that knows how to translate a Python string into run
    content elements appended to a specified ``<w:r>`` element. Contiguous
    sequences of regular characters are appended in a single ``<w:t>``
    element. Each tab character ('\t') causes a ``<w:tab/>`` element to be
    appended. Likewise a newline or carriage return character ('\n', '\r')
    causes a ``<w:cr>`` element to be appended.
    """
    def __init__(self, r):
        self._r = r
        self._bfr = []

    @classmethod
    def append_to_run_from_text(cls, r, text):
        """
        Create a "one-shot" ``_RunContentAppender`` instance and use it to
        append the run content elements corresponding to *text* to the
        ``<w:r>`` element *r*.
        """
        appender = cls(r)
        appender.add_text(text)

    def add_text(self, text):
        """
        Append the run content elements corresponding to *text* to the
        ``<w:r>`` element of this instance.
        """
        for char in text:
            self.add_char(char)
        self.flush()

    def add_char(self, char):
        """
        Process the next character of input through the translation finite
        state maching (FSM). There are two possible states, buffer pending
        and not pending, but those are hidden behind the ``.flush()`` method
        which must be called at the end of text to ensure any pending
        ``<w:t>`` element is written.
        """
        if char == '\t':
            self.flush()
            self._r.add_tab()
        elif char in '\r\n':
            self.flush()
            self._r.add_br()
        else:
            self._bfr.append(char)

    def flush(self):
        text = ''.join(self._bfr)
        if text:
            self._r.add_t(text)
        del self._bfr[:]

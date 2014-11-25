# encoding: utf-8

"""
Test suite for the docx.oxml.text module.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import pytest

from docx.exceptions import InvalidSpanError
from docx.oxml import parse_xml
from docx.oxml.table import CT_Row, CT_Tc

from ..unitutil.cxml import element
from ..unitutil.file import snippet_seq
from ..unitutil.mock import instance_mock, method_mock, property_mock


class DescribeCT_Row(object):

    def it_raises_on_tc_at_grid_col(self, tc_raise_fixture):
        tr, idx = tc_raise_fixture
        with pytest.raises(ValueError):
            tr.tc_at_grid_col(idx)

    # fixtures -------------------------------------------------------

    @pytest.fixture(params=[(0, 0, 3), (1, 0, 1)])
    def tc_raise_fixture(self, request):
        snippet_idx, row_idx, col_idx = request.param
        tbl = parse_xml(snippet_seq('tbl-cells')[snippet_idx])
        tr = tbl.tr_lst[row_idx]
        return tr, col_idx


class DescribeCT_Tc(object):

    def it_can_merge_to_another_tc(self, merge_fixture):
        tc, other_tc, top_tr_, top_tc_, left, height, width = merge_fixture
        merged_tc = tc.merge(other_tc)
        tc._span_dimensions.assert_called_once_with(other_tc)
        top_tr_.tc_at_grid_col.assert_called_once_with(left)
        top_tc_._grow_to.assert_called_once_with(width, height)
        assert merged_tc is top_tc_

    def it_knows_its_extents_to_help(self, extents_fixture):
        tc, attr_name, expected_value = extents_fixture
        extent = getattr(tc, attr_name)
        assert extent == expected_value

    def it_calculates_the_dimensions_of_a_span_to_help(self, span_fixture):
        tc, other_tc, expected_dimensions = span_fixture
        dimensions = tc._span_dimensions(other_tc)
        assert dimensions == expected_dimensions

    def it_raises_on_invalid_span(self, span_raise_fixture):
        tc, other_tc = span_raise_fixture
        with pytest.raises(InvalidSpanError):
            tc._span_dimensions(other_tc)

    def it_raises_on_tr_above(self, tr_above_raise_fixture):
        tc = tr_above_raise_fixture
        with pytest.raises(ValueError):
            tc._tr_above

    # fixtures -------------------------------------------------------

    @pytest.fixture(params=[
        (0, 0, 0, 'top',    0), (2, 0, 1, 'top',    0),
        (2, 1, 1, 'top',    0), (4, 2, 1, 'top',    1),
        (0, 0, 0, 'left',   0), (1, 0, 1, 'left',   2),
        (3, 1, 0, 'left',   0), (3, 1, 1, 'left',   2),
        (0, 0, 0, 'bottom', 1), (1, 0, 0, 'bottom', 1),
        (2, 0, 1, 'bottom', 2), (4, 1, 1, 'bottom', 3),
        (0, 0, 0, 'right',  1), (1, 0, 0, 'right',  2),
        (0, 0, 0, 'right',  1), (4, 2, 1, 'right',  3),
    ])
    def extents_fixture(self, request):
        snippet_idx, row, col, attr_name, expected_value = request.param
        tbl = self._snippet_tbl(snippet_idx)
        tc = tbl.tr_lst[row].tc_lst[col]
        return tc, attr_name, expected_value

    @pytest.fixture
    def merge_fixture(
            self, tr_, _span_dimensions_, _tbl_, _grow_to_, top_tc_):
        tc, other_tc = element('w:tc'), element('w:tc')
        top, left, height, width = 0, 1, 2, 3
        _span_dimensions_.return_value = top, left, height, width
        _tbl_.return_value.tr_lst = [tr_]
        tr_.tc_at_grid_col.return_value = top_tc_
        return tc, other_tc, tr_, top_tc_, left, height, width

    @pytest.fixture(params=[
        (0, 0, 0, 0, 1, (0, 0, 1, 2)),
        (0, 0, 1, 2, 1, (0, 1, 3, 1)),
        (0, 2, 2, 1, 1, (1, 1, 2, 2)),
        (0, 1, 2, 1, 0, (1, 0, 1, 3)),
        (1, 0, 0, 1, 1, (0, 0, 2, 2)),
        (1, 0, 1, 0, 0, (0, 0, 1, 3)),
        (2, 0, 1, 2, 1, (0, 1, 3, 1)),
        (2, 0, 1, 1, 0, (0, 0, 2, 2)),
        (2, 1, 2, 0, 1, (0, 1, 2, 2)),
        (4, 0, 1, 0, 0, (0, 0, 1, 3)),
    ])
    def span_fixture(self, request):
        snippet_idx, row, col, row_2, col_2, expected_value = request.param
        tbl = self._snippet_tbl(snippet_idx)
        tc = tbl.tr_lst[row].tc_lst[col]
        tc_2 = tbl.tr_lst[row_2].tc_lst[col_2]
        return tc, tc_2, expected_value

    @pytest.fixture(params=[
        (1, 0, 0, 1, 0),  # inverted-L horz
        (1, 1, 0, 0, 0),  # same in opposite order
        (2, 0, 2, 0, 1),  # inverted-L vert
        (5, 0, 1, 1, 0),  # tee-shape horz bar
        (5, 1, 0, 2, 1),  # same, opposite side
        (6, 1, 0, 0, 1),  # tee-shape vert bar
        (6, 0, 1, 1, 2),  # same, opposite side
    ])
    def span_raise_fixture(self, request):
        snippet_idx, row, col, row_2, col_2 = request.param
        tbl = self._snippet_tbl(snippet_idx)
        tc = tbl.tr_lst[row].tc_lst[col]
        tc_2 = tbl.tr_lst[row_2].tc_lst[col_2]
        print(tc.top, tc_2.top, tc.bottom, tc_2.bottom)
        return tc, tc_2

    @pytest.fixture(params=[(0, 0, 0), (4, 0, 0)])
    def tr_above_raise_fixture(self, request):
        snippet_idx, row_idx, col_idx = request.param
        tbl = parse_xml(snippet_seq('tbl-cells')[snippet_idx])
        tc = tbl.tr_lst[row_idx].tc_lst[col_idx]
        return tc

    # fixture components ---------------------------------------------

    @pytest.fixture
    def _grow_to_(self, request):
        return method_mock(request, CT_Tc, '_grow_to')

    @pytest.fixture
    def _span_dimensions_(self, request):
        return method_mock(request, CT_Tc, '_span_dimensions')

    def _snippet_tbl(self, idx):
        """
        Return a <w:tbl> element for snippet at *idx* in 'tbl-cells' snippet
        file.
        """
        return parse_xml(snippet_seq('tbl-cells')[idx])

    @pytest.fixture
    def _tbl_(self, request):
        return property_mock(request, CT_Tc, '_tbl')

    @pytest.fixture
    def top_tc_(self, request):
        return instance_mock(request, CT_Tc)

    @pytest.fixture
    def tr_(self, request):
        return instance_mock(request, CT_Row)
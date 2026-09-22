"""Regression coverage for ERS's old grouped and new column-based workbooks."""
import io
import unittest
import zipfile
from xml.sax.saxutils import escape

from chartbook.clients.ers_trade_client import _parse_workbook


def workbook(rows):
    output = io.BytesIO()
    cells = []
    for number, row in enumerate(rows, 1):
        cells.append('<row>' + ''.join(
            f'<c r="{column}{number}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
            for column, value in row.items()
        ) + '</row>')
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr('xl/workbook.xml', '''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
            <sheets><sheet name="Trade" sheetId="1" r:id="rId1"/></sheets></workbook>''')
        archive.writestr('xl/_rels/workbook.xml.rels', '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
            <Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>''')
        archive.writestr('xl/worksheets/sheet1.xml',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
            + ''.join(cells) + '</sheetData></worksheet>')
    return output.getvalue()


class TradeWorkbookTests(unittest.TestCase):
    def test_legacy_section_header_also_contains_country(self):
        totals, countries = _parse_workbook(workbook([
            {'A': 'Import/export, geography code and name', 'D': 'Jun-26', 'E': 'Jul-26'},
            {'A': 'Shell-egg exports (1,000 dozen)', 'B': '1220', 'C': 'Canada', 'D': '10', 'E': '12'},
            {'C': 'Total', 'D': '10', 'E': '12'},
        ]), 'fixture')
        self.assertEqual([r['value'] for r in totals], [10, 12])
        self.assertEqual([r['report_month'] for r in countries], ['2026-06', '2026-07'])
        self.assertEqual(countries[0]['geography_name'], 'Canada')

    def test_new_layout_world_total_and_both_flows(self):
        rows = [{'A': 'Commodity description', 'B': 'Trade flow', 'C': 'Unit description',
                 'D': 'Geography code', 'E': 'Geography description', 'F': 'Jul-26'}]
        for flow, value in [('Imports', '4'), ('Exports', '12')]:
            rows += [
                {'A': 'Shell-egg', 'B': flow, 'C': '1,000 dozen', 'D': '1220', 'E': 'Canada', 'F': value},
                {'A': 'Shell-egg', 'B': flow, 'C': '1,000 dozen', 'D': '', 'E': 'World total', 'F': value},
            ]
        rows.append({'A': 'Turkey', 'B': 'Exports', 'C': '1,000 pounds', 'E': 'World total', 'F': '999'})
        totals, countries = _parse_workbook(workbook(rows), 'fixture')
        self.assertEqual([(r['flow'], r['value']) for r in totals], [('import', 4), ('export', 12)])
        self.assertEqual(len(countries), 2)
        self.assertTrue(all(r['product'] == 'shell_egg' for r in totals))

    def test_unrecognized_layout_does_not_silently_succeed(self):
        with self.assertRaisesRegex(ValueError, 'No ERS trade totals'):
            _parse_workbook(workbook([{'A': 'Unknown header'}]), 'fixture')

    def test_wrong_units_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unexpected ERS trade unit'):
            _parse_workbook(workbook([
                {'A': 'Commodity description', 'F': 'Jul-26'},
                {'A': 'Shell-egg', 'B': 'Exports', 'C': 'pounds', 'E': 'World total', 'F': '12'},
            ]), 'fixture')


if __name__ == '__main__':
    unittest.main()

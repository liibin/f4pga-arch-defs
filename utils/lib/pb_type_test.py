#!/usr/bin/env python3

from io import StringIO
import unittest

import lxml.etree as ET

import pb_type


class TestFindLeafBlifAttribute(unittest.TestCase):
    def test_not_found(self):
        xml = ET.parse(
            StringIO("""\
<pb_type name="top" num_pb="1"></pb_type>
""")
        )
        self.assertIsNone(pb_type.find_leaf(xml.getroot()))

    def test_top_subckt(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1" blif_model=".subckt abc"></pb_type>
"""
            )
        )
        r = xml.getroot()
        self.assertIs(r, pb_type.find_leaf(r))

    def test_top_lut(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1" blif_model=".names"></pb_type>
"""
            )
        )
        r = xml.getroot()
        self.assertIs(r, pb_type.find_leaf(r))

    def test_prefix_spaces(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1" blif_model="   .subckt abc"></pb_type>
"""
            )
        )
        r = xml.getroot()
        self.assertIs(r, pb_type.find_leaf(r))

    def test_suffix_spaces(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1" blif_model=".subckt abc   "></pb_type>
"""
            )
        )
        r = xml.getroot()
        self.assertIs(r, pb_type.find_leaf(r))

    def test_leaf_subckt(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1">
  <pb_type name="middle" num_pb="1">
    <pb_type name="leaf" num_pb="1" blif_model=".subckt abc">
    </pb_type>
  </pb_type>
</pb_type>
"""
            )
        )
        r = xml.getroot()
        leaf = xml.find("//pb_type[@name='leaf']")
        assert leaf is not None
        self.assertIs(leaf, pb_type.find_leaf(r))

    def test_leaf_lut(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1">
  <pb_type name="middle" num_pb="1">
    <pb_type name="leaf" num_pb="1" blif_model=".names">
    </pb_type>
  </pb_type>
</pb_type>
"""
            )
        )
        r = xml.getroot()
        leaf = xml.find("//pb_type[@name='leaf']")
        assert leaf is not None
        self.assertIs(leaf, pb_type.find_leaf(r))


class TestFindLeafBlifTag(unittest.TestCase):
    def test_top_subckt(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1">
  <blif_model>.subckt abc</blif_model>
</pb_type>
"""
            )
        )
        r = xml.getroot()
        self.assertIs(r, pb_type.find_leaf(r))

    def test_top_lut(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1">
  <blif_model>.names</blif_model>
</pb_type>
"""
            )
        )
        r = xml.getroot()
        self.assertIs(r, pb_type.find_leaf(r))

    def test_prefix_spaces(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1">
  <blif_model>   .subckt abc</blif_model>
</pb_type>
"""
            )
        )
        r = xml.getroot()
        self.assertIs(r, pb_type.find_leaf(r))

    def test_suffix_spaces(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1">
  <blif_model>.subckt abc   </blif_model>
</pb_type>
"""
            )
        )
        r = xml.getroot()
        self.assertIs(r, pb_type.find_leaf(r))

    def test_leaf_subckt(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1">
  <pb_type name="middle" num_pb="1">
    <pb_type name="leaf" num_pb="1">
      <blif_model>.subckt abc</blif_model>
    </pb_type>
  </pb_type>
</pb_type>
"""
            )
        )
        r = xml.getroot()
        leaf = xml.find("//pb_type[@name='leaf']")
        assert leaf is not None
        self.assertIs(leaf, pb_type.find_leaf(r))

    def test_leaf_lut(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="top" num_pb="1">
  <pb_type name="middle" num_pb="1">
    <pb_type name="leaf" num_pb="1" blif_model=".names">
    </pb_type>
  </pb_type>
</pb_type>
"""
            )
        )
        r = xml.getroot()
        leaf = xml.find("//pb_type[@name='leaf']")
        assert leaf is not None
        self.assertIs(leaf, pb_type.find_leaf(r))


class TestPorts(unittest.TestCase):
    def test_simple(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="AUSED" num_pb="1">
  <input name="I0" num_pins="1"/>
  <output name="O" num_pins="1"/>
</pb_type>
"""
            )
        )
        name, clocks, inputs, outputs, carry = pb_type.ports(xml.getroot())

        self.assertEqual("AUSED", name)
        self.assertListEqual(clocks, [])
        self.assertListEqual(inputs, [('I0', 1)])
        self.assertListEqual(outputs, [('O', 1)])
        self.assertDictEqual(carry, {})

    def test_clock(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="DFF" num_pb="1">
  <clock name="C" num_pins="1"/>
  <input name="D" num_pins="1"/>
  <output name="Q" num_pins="1"/>
</pb_type>
"""
            )
        )
        name, clocks, inputs, outputs, carry = pb_type.ports(xml.getroot())

        self.assertEqual("DFF", name)
        self.assertListEqual(clocks, [('C', 1)])
        self.assertListEqual(inputs, [('D', 1)])
        self.assertListEqual(outputs, [('Q', 1)])
        self.assertDictEqual(carry, {})

    def test_width(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="XXX" num_pb="1">
  <clock  name="C1" num_pins="2"/>
  <clock  name="C2" num_pins="4"/>
  <clock  name="C3" num_pins="8"/>
  <input  name="D1" num_pins="3"/>
  <input  name="D2" num_pins="5"/>
  <output name="Q1" num_pins="7"/>
  <output name="Q2" num_pins="9"/>
</pb_type>
"""
            )
        )
        name, clocks, inputs, outputs, carry = pb_type.ports(xml.getroot())

        self.assertEqual("XXX", name)
        self.assertListEqual(clocks, [('C1', 2), ('C2', 4), ('C3', 8)])
        self.assertListEqual(inputs, [('D1', 3), ('D2', 5)])
        self.assertListEqual(outputs, [('Q1', 7), ('Q2', 9)])
        self.assertDictEqual(carry, {})

    def test_carry(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="XXX" num_pb="1">
  <input  name="D1" num_pins="1">
    <pack_pattern type="carry" name="C1" />
  </input>
  <input  name="D2" num_pins="5"/>
  <output name="Q1" num_pins="7">
    <pack_pattern type="pack" />
  </output>
  <output name="Q2" num_pins="1">
    <pack_pattern type="carry" name="C1" />
  </output>
</pb_type>
"""
            )
        )
        name, clocks, inputs, outputs, carry = pb_type.ports(xml.getroot())

        self.assertEqual("XXX", name)
        self.assertListEqual(clocks, [])
        self.assertListEqual(inputs, [('D2', 5)])
        self.assertListEqual(outputs, [('Q1', 7)])
        self.assertDictEqual(carry, {'C1': ('D1', 'Q2')})

    def test_morecarry(self):
        xml = ET.parse(
            StringIO(
                """\
<pb_type name="XXX" num_pb="1">
  <input  name="D1" num_pins="1">
    <pack_pattern type="carry" name="C1" />
  </input>
  <input  name="D2" num_pins="5"/>
  <input  name="D3" num_pins="1">
    <pack_pattern type="carry" name="C2" />
  </input>
  <output name="Q1" num_pins="7">
    <pack_pattern type="pack" />
  </output>
  <output name="Q2" num_pins="1">
    <pack_pattern type="carry" name="C2" />
  </output>
  <output name="Q3" num_pins="1">
    <pack_pattern type="carry" name="C1" />
  </output>
</pb_type>
"""
            )
        )
        name, clocks, inputs, outputs, carry = pb_type.ports(xml.getroot())

        self.assertEqual("XXX", name)
        self.assertListEqual(clocks, [])
        self.assertListEqual(inputs, [('D2', 5)])
        self.assertListEqual(outputs, [('Q1', 7)])
        self.assertDictEqual(carry, {'C1': ('D1', 'Q3'), 'C2': ('D3', 'Q2')})


if __name__ == "__main__":
    unittest.main(verbosity=2)

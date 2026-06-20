import xml.etree.ElementTree as ET

def validate_pnml(pnml_string):
    try:
        root = ET.fromstring(pnml_string)
        
        # Check if the root element is 'pnml'
        if root.tag != 'pnml':
            return 'Invalid: Root element is not <pnml>'
        
        # Check for required elements and attributes
        nets = root.findall('net')
        if not nets:
            return 'Invalid: No <net> elements found'
        
        for net in nets:
            if 'id' not in net.attrib or 'type' not in net.attrib:
                return 'Invalid: <net> element missing required attributes'
            
            places = net.findall('place')
            transitions = net.findall('transition')
            arcs = net.findall('arc')
            
            if not places:
                return 'Invalid: No <place> elements found in <net>'
            if not transitions:
                return 'Invalid: No <transition> elements found in <net>'
            if not arcs:
                return 'Invalid: No <arc> elements found in <net>'
        
        # If all checks pass
        return 'Valid PNML'
    except ET.ParseError:
        return 'Invalid: Not a well-formed XML'

# Example usage:
pnml_example_string = """
<pnml>
  <net id="net1" type="http://www.pnml.org/version-2009/grammar/pnmlcoremodel">
    <place id="p1"/>
    <transition id="t1"/>
    <arc id="a1" source="p1" target="t1"/>
  </net>
</pnml>
"""

pnml_base_model_string = """
<pnml>
  <net type="http://www.informatik.hu-berlin.de/top/pntd/ptNetb" id="noID">
    <place id="p1">
      <name>
        <text>detection</text>
        <graphics>
          <offset x="50" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="50" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
      <initialMarking>
        <text>1</text>
      </initialMarking>
    </place>
    <place id="p2">
      <name>
        <text>open</text>
        <graphics>
          <offset x="200" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="200" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
    </place>
    <place id="p6">
      <name>
        <text>notification</text>
        <graphics>
          <offset x="500" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="500" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
    </place>
    <place id="p7">
      <name>
        <text>closing_code</text>
        <graphics>
          <offset x="650" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="650" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
    </place>
    <place id="p8">
      <name>
        <text>resolution</text>
        <graphics>
          <offset x="350" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="350" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
    </place>
    <transition id="t4">
      <name>
        <text>A</text>
        <graphics>
          <offset x="270" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="275" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
      <toolspecific tool="WoPeD" version="1.0">
        <time>0</time>
        <timeUnit>1</timeUnit>
        <orientation>1</orientation>
      </toolspecific>
    </transition>
    <transition id="t6">
      <name>
        <text>R</text>
        <graphics>
          <offset x="420" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="425" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
      <toolspecific tool="WoPeD" version="1.0">
        <time>0</time>
        <timeUnit>1</timeUnit>
        <orientation>1</orientation>
      </toolspecific>
    </transition>
    <transition id="t7">
      <name>
        <text>C</text>
        <graphics>
          <offset x="570" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="575" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
      <toolspecific tool="WoPeD" version="1.0">
        <time>0</time>
        <timeUnit>1</timeUnit>
        <orientation>1</orientation>
      </toolspecific>
    </transition>
    <transition id="t1">
      <name>
        <text>N</text>
        <graphics>
          <offset x="120" y="110"/>
        </graphics>
      </name>
      <graphics>
        <position x="125" y="70"/>
        <dimension x="40" y="40"/>
      </graphics>
      <toolspecific tool="WoPeD" version="1.0">
        <time>0</time>
        <timeUnit>1</timeUnit>
        <orientation>1</orientation>
      </toolspecific>
    </transition>
    <arc id="a261" source="p1" target="t1">
      <inscription>
        <text>1</text>
        <graphics>
          <offset x="500.0" y="-12.0"/>
        </graphics>
      </inscription>
      <graphics/>
      <toolspecific tool="WoPeD" version="1.0">
        <probability>1.0</probability>
        <displayProbabilityOn>false</displayProbabilityOn>
        <displayProbabilityPosition x="500.0" y="12.0"/>
      </toolspecific>
    </arc>
    <arc id="a11" source="p8" target="t6">
      <inscription>
        <text>1</text>
        <graphics>
          <offset x="500.0" y="-12.0"/>
        </graphics>
      </inscription>
      <graphics/>
      <toolspecific tool="WoPeD" version="1.0">
        <probability>1.0</probability>
        <displayProbabilityOn>false</displayProbabilityOn>
        <displayProbabilityPosition x="500.0" y="12.0"/>
      </toolspecific>
    </arc>
    <arc id="a262" source="t1" target="p2">
      <inscription>
        <text>1</text>
        <graphics>
          <offset x="500.0" y="-12.0"/>
        </graphics>
      </inscription>
      <graphics/>
      <toolspecific tool="WoPeD" version="1.0">
        <probability>1.0</probability>
        <displayProbabilityOn>false</displayProbabilityOn>
        <displayProbabilityPosition x="500.0" y="12.0"/>
      </toolspecific>
    </arc>
    <arc id="a10" source="t4" target="p8">
      <inscription>
        <text>1</text>
        <graphics>
          <offset x="500.0" y="-12.0"/>
        </graphics>
      </inscription>
      <graphics/>
      <toolspecific tool="WoPeD" version="1.0">
        <probability>1.0</probability>
        <displayProbabilityOn>false</displayProbabilityOn>
        <displayProbabilityPosition x="500.0" y="12.0"/>
      </toolspecific>
    </arc>
    <arc id="a263" source="p2" target="t4">
      <inscription>
        <text>1</text>
        <graphics>
          <offset x="500.0" y="-12.0"/>
        </graphics>
      </inscription>
      <graphics/>
      <toolspecific tool="WoPeD" version="1.0">
        <probability>1.0</probability>
        <displayProbabilityOn>false</displayProbabilityOn>
        <displayProbabilityPosition x="500.0" y="12.0"/>
      </toolspecific>
    </arc>
    <arc id="a265" source="t6" target="p6">
      <inscription>
        <text>1</text>
        <graphics>
          <offset x="500.0" y="-12.0"/>
        </graphics>
      </inscription>
      <graphics/>
      <toolspecific tool="WoPeD" version="1.0">
        <probability>1.0</probability>
        <displayProbabilityOn>false</displayProbabilityOn>
        <displayProbabilityPosition x="500.0" y="12.0"/>
      </toolspecific>
    </arc>
    <arc id="a266" source="p6" target="t7">
      <inscription>
        <text>1</text>
        <graphics>
          <offset x="500.0" y="-12.0"/>
        </graphics>
      </inscription>
      <graphics/>
      <toolspecific tool="WoPeD" version="1.0">
        <probability>1.0</probability>
        <displayProbabilityOn>false</displayProbabilityOn>
        <displayProbabilityPosition x="500.0" y="12.0"/>
      </toolspecific>
    </arc>
    <arc id="a267" source="t7" target="p7">
      <inscription>
        <text>1</text>
        <graphics>
          <offset x="500.0" y="-12.0"/>
        </graphics>
      </inscription>
      <graphics/>
      <toolspecific tool="WoPeD" version="1.0">
        <probability>1.0</probability>
        <displayProbabilityOn>false</displayProbabilityOn>
        <displayProbabilityPosition x="500.0" y="12.0"/>
      </toolspecific>
    </arc>
    <toolspecific tool="WoPeD" version="1.0">
      <bounds>
        <position x="2" y="27"/>
        <dimension x="2539" y="1119"/>
      </bounds>
      <scale>101</scale>
      <treeWidthRight>2066</treeWidthRight>
      <overviewPanelVisible>true</overviewPanelVisible>
      <treeHeightOverview>100</treeHeightOverview>
      <treePanelVisible>true</treePanelVisible>
      <verticalLayout>false</verticalLayout>
      <resources/>
      <simulations/>
      <partnerLinks/>
      <variables/>
    </toolspecific>
  </net>
</pnml>
"""

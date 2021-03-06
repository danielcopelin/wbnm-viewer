import re
from dataclasses import dataclass
from itertools import zip_longest
from typing import Optional


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


class Runfile:

    def __init__(self, file_path):
        self.file_path = file_path
        self.contents = self.read()
        self.preamble = PreambleBlock(self.contents)
        self.status = StatusBlock(self.contents)
        self.display = DisplayBlock(self.contents)
        self.topology = TopologyBlock(self.contents)
        self.surfaces = SurfacesBlock(self.contents)
        self.flowpaths = FlowpathsBlock(self.contents)

    def read(self):
        with open(self.file_path, 'r') as runfile:
            contents = runfile.readlines()
        return contents

    # def commit(self):
    #     with open(self.file_path, 'w') as runfile:
    #         self.preamble.write()
    #         self.all_the_other_sections.write()


class RunfileBlock:

    start_line = 'STARTLINE'
    end_line = 'ENDLINE'

    def __init__(self, runfile_contents):
        self.runfile_contents = runfile_contents
        self.block_contents = self.read()

    def read(self):
        start = re.compile(re.escape(self.start_line))
        end = re.compile(re.escape(self.end_line))
        block_contents = []
        inside_block = False
        for line in self.runfile_contents:
            if inside_block:
                if re.match(end, line):
                    inside_block = False
                else:
                    block_contents.append(line)
            elif re.match(start, line):
                inside_block = True
        return block_contents


class PreambleBlock(RunfileBlock):

    start_line = '#####START_PREAMBLE_BLOCK##########|###########|###########|###########|'
    end_line = '#####END_PREAMBLE_BLOCK############|###########|###########|###########|'


class StatusBlock(RunfileBlock):

    start_line = '#####START_STATUS_BLOCK############|###########|###########|###########|'
    end_line = '#####END_STATUS_BLOCK##############|###########|###########|###########|'

    def __init__(self, runfile_contents):
        super().__init__(runfile_contents)
        self.pathname, self.date_last_edit, self.name, selfversion_number = self.block_contents


class DisplayBlock(RunfileBlock):

    start_line = '#####START_DISPLAY_BLOCK###########|###########|###########|###########|'
    end_line = '#####END_DISPLAY_BLOCK#############|###########|###########|###########|'

    def __init__(self, runfile_contents):
        super().__init__(runfile_contents)
        self.window_coords = self.block_contents[0].split()
        self.gis_map_filename = self.block_contents[1]
        self.map_coords = self.block_contents[2].split()


@dataclass
class CatchmentTopology:
    name: str
    cg_e: str
    cg_n: str
    outlet_e: str
    outlet_n: str
    downstream_sub_name: str


class TopologyBlock(RunfileBlock):

    start_line = '#####START_TOPOLOGY_BLOCK##########|###########|###########|###########|'
    end_line = '#####END_TOPOLOGY_BLOCK############|###########|###########|###########|'

    def __init__(self, runfile_contents):
        super().__init__(runfile_contents)

        self.num_subareas, self.catchment_name = re.search(re.compile('([0-9]+)\s*(.*)'), self.block_contents[0]).groups()
        self.topology = {}
        for catchment_topology_line in self.block_contents[1:]:
            name = catchment_topology_line.split()[0]
            self.topology[name] = CatchmentTopology(*catchment_topology_line.split())


@dataclass
class CatchmentSurface:
    name: str
    area: str
    imp: str
    lag: str
    imp_lag: str


class SurfacesBlock(RunfileBlock):

    start_line = '#####START_SURFACES_BLOCK##########|###########|###########|###########|'
    end_line = '#####END_SURFACES_BLOCK############|###########|###########|###########|'

    def __init__(self, runfile_contents):
        super().__init__(runfile_contents)

        self.nonlinearity_exponent = self.block_contents[0]
        self.discharge_when_routing_switches = self.block_contents[0]
        self.surfaces = {}
        for catchment_surface_line in self.block_contents[2:]:
            name = catchment_surface_line.split()[0]
            self.surfaces[name] = CatchmentSurface(*catchment_surface_line.split())


@dataclass
class CatchmentFlowpath:
    name: str
    routing_type: str
    stream_lag: Optional[str] = None
    delay: Optional[str] = None
    musk_k: Optional[str] = None
    musk_x: Optional[str] = None


class FlowpathsBlock(RunfileBlock):

    start_line = '#####START_FLOWPATHS_BLOCK#########|###########|###########|###########|'
    end_line = '#####END_FLOWPATHS_BLOCK###########|###########|###########|###########|'

    routing_types = {
        '#####ROUTING': 'routing',
        '#####DELAY': 'delay',
        '#####MUSK': 'musk',
    }

    def __init__(self, runfile_contents):
        super().__init__(runfile_contents)

        self.num_subareas_with_stream = self.block_contents[0]
        self.flowpaths = {}
        for name, routing_line, value in grouper(3, self.block_contents[1:]):
            name = name.strip()
            routing_type = self.routing_types[routing_line.strip()]
            if routing_type == 'routing':
                stream_lag = value.strip()
                self.flowpaths[name] = CatchmentFlowpath(name, routing_type, stream_lag=stream_lag)
            elif routing_type == 'delay':
                delay = value.strip()
                self.flowpaths[name] = CatchmentFlowpath(name, routing_type, delay=delay)
            elif routing_type == 'musk':
                musk_k, musk_x = value.strip().split()
                self.flowpaths[name] = CatchmentFlowpath(name, routing_type, musk_k=musk_k, musk_x=musk_x)


class LocalStructure(RunfileBlock):

    structure_types = {
        '#####H_S_Q': 'hsq',
        '#####H_S': 'hs',
        '#####H_S(TWF)': 'hs_twf',
        '#####H_S(TWR)': 'hs_twr',
        '#####H_S(TWC)': 'hs_twc',
    }

    outlet_types = {
        '#####BOX': 'box',
        '#####PIPE': 'pipe',
        '#####WEIR': 'weir',
        '#####SCOUR': 'scour',
    }

    def __init__(self, local_structure_block_contents, local_structure_no):

        self.start_line = f'#####START_LOCAL_STRUCTURE#{local_structure_no}'
        self.end_line = f'#####END_LOCAL_STRUCTURE#{local_structure_no}'

        super().__init__(local_structure_block_contents)
        self.description = self.block_contents[0].strip()
        self.subarea_name = self.block_contents[1].strip()
        self.structure_type = self.structure_types[self.block_contents[0].strip().split()[1]]

        if self.structure_type


class LocalStructuresBlock(RunfileBlock):

    start_line = '#####START_LOCAL_STRUCTURES_BLOCK##|###########|###########|###########|'
    end_line = '#####END_LOCAL_STRUCTURES_BLOCK####|###########|###########|###########|'

    def __init__(self, runfile_contents):
        super().__init__(runfile_contents)

        self.structures = {}
        self.num_subareas_with_local_structure = self.block_contents[0]

        for n in range(1, self.num_subareas_with_local_structure + 1):
            self.structures[n] = LocalStructure(self.block_contents, n)


if __name__ == "__main__":

    runfile = Runfile(r"test\testrunfile.wbn")
    print(runfile.flowpaths.flowpaths)
    # print(runfile.preamble.block_contents)
    # new_preamble = 'abcdefgh'.split()
    # runfile.preamble.contents = new_preamble

    # runfile.commit()


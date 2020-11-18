import re
from dataclasses import dataclass

class Runfile:

    def __init__(self, file_path):
        self.file_path = file_path
        self.contents = self.read()
        self.preamble = PreambleBlock(self.contents)
        self.status = StatusBlock(self.contents)
        self.display = DisplayBlock(self.contents)
        self.topology = TopologyBlock(self.contents)
        self.surfaces = SurfacesBlock(self.contents)

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
class CatchmentRouting:
    name: str
    routing_type: str
    stream_lag: str
    delay: str
    musk_k: str
    musk_x: str


class FlowpathsBlock(RunfileBlock):

    start_line = '#####START_FLOWPATHS_BLOCK#########|###########|###########|###########|'
    end_line = '#####END_FLOWPATHS_BLOCK###########|###########|###########|############|'

    def __init__(self, runfile_contents):
        super().__init__(runfile_contents)

        self.num_subareas_with_stream = self.block_contents[0]
        self.discharge_when_routing_switches = self.block_contents[0]
        self.flowpaths = {}
        for line in self.block_contents[1:]:
            name = catchment_surface_line.split()[0]
            self.surfaces[name] = CatchmentSurface(*catchment_surface_line.split())


if __name__ == "__main__":

    runfile = Runfile(r"test\testrunfile.wbn")
    # print(runfile.preamble.block_contents)
    # new_preamble = 'abcdefgh'.split()
    # runfile.preamble.contents = new_preamble

    # runfile.commit()


import argparse
from pathlib import Path

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import (
    BinaryResource,
    SimpointResource,
)
from gem5.resources.workload import Workload
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.exit_event_generators import save_checkpoint_generator
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

requires(isa_required=ISA.X86)

parser = argparse.ArgumentParser(
    description="Generates checkpoints from simpoints"
)

parser.add_argument(
	"--binary",
	type=str,
	required=True,
	help="The binary to simulate.",
)

parser.add_argument(
	"--arguments",
	type=str,
	required=False,
	default="",
	help="The arguments to the binary for simulation."
)

parser.add_argument(
	"--simpoints",
	type=str,
	required=True,
	help="The simpoint file.",
)

parser.add_argument(
	"--weights",
	type=str,
	required=True,
	help="The weights file.",
)

parser.add_argument(
	"--interval",
	type=int,
	required=False,
	default=100_000_000,
	help="The size of an interval in instructions.",
)

parser.add_argument(
	"--warmup",
	type=int,
	required=False,
	default=50_000_000,
	help="The size of the warmup in instructions.",
)

parser.add_argument(
    "--checkpoint-dir",
    type=str,
    required=True,
    help="The directory to store the checkpoints.",
)

args = parser.parse_args()

cache_hierarchy = NoCache()

memory = SingleChannelDDR3_1600(size="2GB")

processor = SimpleProcessor(
    cpu_type=CPUTypes.ATOMIC,
    isa=ISA.X86,
    num_cores=1,
)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

def parse_simpoint_file(path):
	with open(path, "r") as file:
		return [line.split()[0] for line in file.readlines()]

simpoints = [int(e) for e in parse_simpoint_file(args.simpoints)]
weights = [float(e) for e in parse_simpoint_file(args.weights)]

board.set_se_simpoint_workload(
    binary=BinaryResource(
    	local_path=args.binary,
    	architecture=ISA.X86,
    ),
    arguments=args.arguments.split(),
    simpoint=SimpointResource(
        simpoint_interval=args.interval,
        simpoint_list=simpoints,
        weight_list=weights,
        warmup_interval=args.warmup,
    ),
)

dir = Path(args.checkpoint_dir)

print(args.warmup)

simulator = Simulator(
    board=board,
    on_exit_event={
        # using the SimPoints event generator in the standard library to take
        # checkpoints
        ExitEvent.SIMPOINT_BEGIN: save_checkpoint_generator(dir)
    },
)

simulator.run()
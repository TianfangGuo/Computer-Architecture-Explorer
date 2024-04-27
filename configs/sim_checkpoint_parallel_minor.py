import argparse
from pathlib import Path

from m5.stats import (
	dump,
	reset,
)

from m5.objects.BranchPredictor import (
	LocalBP,
	BiModeBP,
	TAGE,
	MultiperspectivePerceptron8KB,
)

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
	PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import (
	BinaryResource,
	SimpointResource,
	CheckpointResource,
)
from gem5.resources.workload import Workload
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

requires(isa_required=ISA.X86)

parser = argparse.ArgumentParser(
	description="Simulates one checkpoint"
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
	"--checkpoint",
	type=str,
	required=True,
	help="The path to the checkpoint. Expects a directory with pmem file and cpt file.",
)

parser.add_argument(
	"--l1size",
	type=str,
	required=False,
	default="32kB",
	help="Size of the L1 data cache.",
)

parser.add_argument(
	"--l2size",
	type=str,
	required=False,
	default="512kB",
	help="Size of the L2 cache.",
)

parser.add_argument(
	"--pred",
	type=str,
	required=False,
	default="perceptron",
	help="Branch Predictor. Can be 'local', 'bimode', 'tage', or 'perceptron'.",
)

parser.add_argument(
	"--robsize",
	type=int,
	required=False,
	default=128,
	help="Size of the reorder buffer.",
)

parser.add_argument(
	"--regcount",
	type=int,
	required=False,
	default=128,
	help="Number of physical registers.",
)

parser.add_argument(
	"--alucount",
	type=int,
	required=False,
	default=4,
	help="Number of ALUs",
)

parser.add_argument(
	"--mdcount",
	type=int,
	required=False,
	default=4,
	help="Number of multiplier/divider units.",
)

args = parser.parse_args()

# The cache hierarchy can be different from the cache hierarchy used in taking
# the checkpoints
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
	l1d_size=args.l1size,
	l1i_size="64kB",
	l2_size=args.l2size,
	mshrs_size=20,
)

# The memory structure can be different from the memory structure used in
# taking the checkpoints, but the size of the memory must be maintained
memory = DualChannelDDR4_2400(size="2GB")

processor = SimpleProcessor(
	cpu_type=CPUTypes.O3,
	isa=ISA.X86,
	num_cores=1,
)

def pred_arg_to_obj(arg):
	if arg == "local":
		return LocalBP()
	elif arg == "bimode":
		return BiModeBP()
	elif arg == "tage":
		return TAGE()
	elif arg == "perceptron":
		return MultiperspectivePerceptron8KB()
	else:
		assert False

processor.cores[0].core.branchPred.value = pred_arg_to_obj(args.pred)
processor.cores[0].core.numROBEntries.value = args.robsize
processor.cores[0].core.numPhysIntRegs.value = args.regcount
processor.cores[0].core.fuPool.FUList[0].count = args.alucount
processor.cores[0].core.fuPool.FUList[1].count = args.mdcount

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
	checkpoint=CheckpointResource(
		local_path=args.checkpoint,
	),
)

def max_inst():
	warmed_up = False
	while True:
		if warmed_up:
			print("end of SimPoint interval")
			yield True
		else:
			print("end of warmup, starting to simulate SimPoint")
			warmed_up = True
			# Schedule a MAX_INSTS exit event during the simulation
			simulator.schedule_max_insts(
				board.get_simpoint().get_simpoint_interval()
			)
			#dump()
			reset()
			yield False


simulator = Simulator(
	board=board,
	on_exit_event={ExitEvent.MAX_INSTS: max_inst()},
)

# Find warmup interval for the supplied checkpoint
def checkpoint_inst_count(checkpoint):
	with open(checkpoint + "/m5.cpt", "r") as file:
		for line in file.readlines():
			parsed_line = line.split("=")
			if parsed_line[0] == "instCnt":
				return int(parsed_line[1])

def simpoint_idx(checkpoint):
	checkpoint_start_inst = checkpoint_inst_count(checkpoint)
	simpoint_start_insts = board.get_simpoint().get_simpoint_start_insts()
	min_diff = -1
	min_idx = -1
	for idx, simpoint_start_inst in enumerate(simpoint_start_insts):
		diff = abs(simpoint_start_inst - checkpoint_start_inst)
		if min_diff == -1 or diff < min_diff:
			min_diff = diff
			min_idx = idx
	assert min_idx > 0 and min_diff > 0 and min_diff < args.interval / 2
	return min_idx

# Schedule a MAX_INSTS exit event before the simulation begins the
# schedule_max_insts function only schedule event when the instruction length
# is greater than 0.
# In here, it schedules an exit event for the first SimPoint's warmup
# instructions
simulator.schedule_max_insts(
	board.get_simpoint().get_warmup_list()[simpoint_idx(args.checkpoint)]
)
simulator.run()

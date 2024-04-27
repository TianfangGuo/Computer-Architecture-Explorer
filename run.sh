#!/bin/bash
parallel (absolute path to gem5 installation)/gem5/build/X86/gem5.opt --outdir results/m5out-{#} \
sim_checkpoint_parallel.py --binary spec_resources/mcf_r_base.gem5-m64 --arguments="(absolute path to spec_resources folder)/spec_resources/inp.in" \
--simpoints spec_resources/mcf_r.simpts --weights spec_resources/mcf_r.weights \
--checkpoint ckpt_gen/mcf_r_50mil/cpt.9585010381680/ {} \
::: --l1size ::: 8kB 32kB 128kB \
::: --l2size ::: 128kB 512kB 2048kB \
::: --pred ::: local tage perceptron \
::: --robsize ::: 32 128 512 \
::: --regcount ::: 128 256 512 \
::: --alucount ::: 1 4 16 \
::: --mdcount ::: 1 4 16
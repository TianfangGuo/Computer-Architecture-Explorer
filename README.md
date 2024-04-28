# Computer-Architecture-Explorer
**NOTE: due to licensing issues we can not provide the SPEC2017.iso image for you, please contact your instructor to obtain this file. For the purpose of this guide we will assume you have this file and it is in the location specified below.**

Please follow [this guide](https://www.gem5.org/documentation/general_docs/building) for installing and building gem5.

For running your own experiments we provide a recommended directory structure below but really any structure works as long as you get the paths correct. (if you use a different structure you will need to modify *run.sh*)

```
experiments/
    |__ gem5/                                                                           # your gem5 installation
    |
    |__ results/                                                                        # simulation results outputted here
    |
    |__ configs/                                                                        # your gem5 configuration scripts
    |       |__ sim_checkpoint_parallel_minor.py
    |       |__ sim_checkpoint_parallel_o3.py
    |       |__ .
    |       |__ .
    |       |__ other custom configs you've created.py
    |
    |__ spec_resources/                                                                 # support files for running SPEC2017 with gem5
    |       |
    |       |__ benchmarks/
    |       |       |__ 505.mcf_r/
    |       |       |       |
    |       |       |       |__ mcf_r_chkpts/
    |       |       |       |       |
    |       |       |       |       |__ mcf_r_1mil/
    |       |       |       |       |       |__ individual checkpoint directories
    |       |       |       |       |      
    |       |       |       |       |__ mcf_r_50mil/
    |       |       |       |               |__ individual checkpoint directories
    |       |       |       |       
    |       |       |       |__ mcf_r.simpts
    |       |       |       |__ mcf_r.weights
    |       |       |       |__ mcf_r_base.gem5-m64
    |       |       |__ .
    |       |       |__ .
    |       |       |__ other benchmarks you've generated the necessary files for/
    |       |
    |       |__ inp.in
    |       |__ spec17.iso 
    |
    |__ run.sh                                                                          # shell script for running the sims

```

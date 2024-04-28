# Computer-Architecture-Explorer
**NOTE: due to licensing issues we can not provide the SPEC2017.iso image for you, please contact your instructor to obtain this file. For the purpose of this guide we will assume you have this file and it is in the location specified below.**

Please follow [this guide](https://www.gem5.org/documentation/general_docs/building) for installing and building gem5.

For running your own experiments we provide a recommended directory structure below but really any structure works as long as you get the paths correct.\
(if you use a different structure you will need to modify *run.sh*)

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

### Step 1: generate simpoints for a benchmark
Gem5 is very slow, in fact it is around 10,000 to 100,000 times slower than the hardware it simulates! So simulate even a single SPEC benchmark in gem5 will take more than a hundred days. Thus we must use a faster method called the [SimPoint Methodology](https://cseweb.ucsd.edu/~calder/simpoint/), which is a technique to profile a workload without needing to run it in its entirety. You may find the SimPoint toolkit, as well as instructions for how to use it [here](https://cseweb.ucsd.edu/~calder/simpoint/software-release.htm); we suggest using valgrind to generate basic block vectors to feed into SimPoint. 

### Step 2: generate checkpoints in gem5
After you have the SimPoint files, you should generate checkpoints for gem5, which are essentially snapshots of the architectural states at some specified point, which you can resume simulation from. We have provided a script for you to generate checkpoints called *gen_checkpoints.py*, you should pass in various files as command line arguments (take a look inside the script to see exactly which ones :D). This process should take a few hours depending on how fast your computer is.

### Step 3: running the simulations
Now that you have your checkpoints, you should use *run.sh* to run your simulations (if you set up your environment exactly like ours this should work automatically). You can edit run.sh to change paths to files as well as pass in different parameters for the python configuration scripts. Once your simulations are running, it will continously output to .../results/. The script will run as many simulations as it can on your computer (one sim for each logical core), so be careful, as your CPU (and likely memory utilization) will hit 100% for as long as the sims are running. Each simulation can take up to 20 minutes (or even longer), but you can stop them at any time, as whenever a simulation finishes the results are immediately available in .../results/m5out-number/. 



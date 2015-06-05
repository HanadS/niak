# NIAK with docker

The recommended way to install NIAK is to use a [docker](https://www.docker.com/) container, which bundles the NIAK library with all of its dependencies. Docker acts as a lightweight virtual machine, and ensures full repeatability of results, regardless of potential upgrades to the production OS. It can be deployed on Linux, Windows or Mac OSX. To run niak with docker on your work station, you will need super user or sudo privilege. Start by installing docker, following the official [docker installation site](https://docs.docker.com/installation/).

**Disclaimer**: Be aware that any user that can execute a "docker run"  command on a machine have access to the complete file system as a super user. It is possible to run a more secure niak/docker setup, we shall have instructions added in the near future.

###Linux
The first step is to create a docker group and add the user that will use docker to that list.

```bash
# If the group already exists, the command will return an error, just ignore it
sudo groupadd docker
# Then add user USERNAME to the docker group
sudo usermod -a -G docker USERNAME
```

For the docker group to become effective, you will need to either restart the system or type:
``` bash
sudo chgrp docker /run/docker.sock
sudo chmod 660 /run/docker.sock
```
All the members of the docker group will have access to the docker service.

The following command will start NIAK with your home directory accessible (the rest of the file system is not accessible):
```bash
xhost +local:niak_machine
docker run -i -t --privileged --rm -h niak_machine --name niak -v /etc/group:/etc/group -v /etc/passwd:/etc/passwd -v /etc/shadow:/etc/shadow  -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY -v $HOME:$HOME --user $UID simexp/niak /bin/bash -c "cd $HOME; source /opt/minc-itk4/minc-toolkit-config.sh; octave --force-gui; /bin/bash"
```

Note that the first execution will be longer, since the simexp/niak mirror has to be downloaded from the internet. All subsequent call to the line should be much faster. Close the GUI and type "exit" in the terminal to stop your session. if somehow the process did not exit properly and docker complains that niak is already running when you restart it, type:
```bash
docker stop niak
docker rm niak
```

The procedure as been tested on Debian 8.0, Ubuntu 14.10, centOS 7 and fedora 20 and we expect it to run smootly on many other Linux distributions.

### Mac OSX

An extra step is needed to start a docker container on OSX. You first need to start a docker daemon using the boot2docker application. You launch it with a mouse click, or type ```open /Application/boot2docker.app ``` in a terminal to the same effect. Full description is available on the [mac install docker page](https://docs.docker.com/installation/mac/).

This will start a bash terminal (as opposed to the standard OSX tcsh) where you will be able to start the simex/niak docker container. Just type

```bash
docker run -i -t --privileged --rm -v $HOME:$HOME  simexp/niak /bin/bash -c "cd $HOME; source /opt/minc-itk4/minc-toolkit-config.sh; octave; /bin/bash"```

in that terminal.

Note that we do not have a procedure to run the octave gui on OSX yet (comming soon!). Also, on OSX, your data input and output has to be under `/Users`, which is the case for `$HOME = /User/your_name`. (Have a look [here](http://stackoverflow.com/questions/26348353/mount-volume-to-docker-image-on-osx), if you really need to access data from other places)



# Manual installation

The following instructions describe how to install NIAK without using docker.

**Matlab/Octave.** NIAK requires a recent version of [Matlab](http://www.mathworks.com/) (proprietary software) or [GNU Octave](http://www.gnu.org/software/octave/index.html) (free open-source software, GNU license). In addition to Matlab/Octave, NIAK depends on the "image processing" and "statistics" toolbox. This comes by default with Matlab. In Octave, it needs to be downloaded from [Octave forge](http://octave.sourceforge.net/index.html).
```matlab
% For a local install, remove the -global flag.
pkg install -auto -global -forge control general signal image io statistics
```

For Octave users, we suggest editing the `~/.octaverc` to change some of octave's default behaviour.
```matlab
% Verbose in real time
more off
% Use the same .mat files as Matlab
default_save_options('-7');
% Set plot engine to gnuplot, to work around an issue with fltk
graphics_toolkit gnuplot
```

**NIAK library**. Download the [latest NIAK release on NITRC](http://www.nitrc.org/frs/download.php/7470/niak-boss-0.13.0.zip), a free open-source software (MIT license). Once the library has been decompressed, all you need to do is to start a Matlab or Octave session and add the NIAK path (with all his subfolders) to your search path. At this stage all pipelines (except the preprocessing pipeline) will work for nifti files. Any manipulation of MINC files will require the installation of the MINC tools (see below). The NIAK archive bundles the [brain connectivity toolbox](https://sites.google.com/site/bctnet/) and [PSOM](http://psom.simexp-lab.org/), which do not need to be installed separately.
```matlab
 path_niak = '/home/toto/niak/';
 P = genpath(path_niak);
 addpath(P);
```

**MINC tools.** To read MINC files or run the fMRI preprocessing pipeline, it is necessary to install the [minc toolkit](http://www.bic.mni.mcgill.ca/ServicesSoftware/ServicesSoftwareMincToolKit) version 1.9.2 (free open-source software, with a custom MIT-like license).

**Test the installation** Follow the [test tutorial](http://niak.simexp-lab.org/niak_tutorial_test.html) to make sure that your installation is working properly.

# Pipeline manager

NIAK is using a pipeline system called [PSOM](http://psom.simexp-lab.org), a free open-source software (MIT license). With PSOM, it is possible to run computations in parallel on a laptop or a supercomputer, restart efficiently analysis or access detailed logs. In all pipelines, the options of psom are set using the field `opt.psom`. The most important parameter is the maximal number of processes that PSOM can run in parallel. More details about PSOM capabilities and configuration can be found in the dedicated [tutorial](http://psom.simexp-lab.org/psom_configuration.html).
```matlab
% Use up to four processes
opt.psom.max_queued = 4;
```
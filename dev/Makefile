GIT_URL=https://github.com
# GIT_URL=https://hub.fgit.cf

clone: binutils gdb dejagnu gcc glibc qemu pk spike

binutils:
	git clone --branch binutils-2_42 ${GIT_URL}/bminor/binutils-gdb.git binutils

gdb:
	git clone --branch gdb-13-branch ${GIT_URL}/bminor/binutils-gdb.git gdb

dejagnu:
	git clone --branch tintin-dev ${GIT_URL}/lhtin/dejagnu.git dejagnu

gcc:
	git clone --branch trunk ${GIT_URL}/gcc-mirror/gcc.git gcc

glibc:
	git clone --branch glibc-2.38 ${GIT_URL}/bminor/glibc.git glibc

newlib:
	git clone --branch newlib-4.3.0 ${GIT_URL}/bminor/newlib.git newlib

qemu:
	wget https://download.qemu.org/qemu-8.2.1.tar.xz
	tar xvJf qemu-8.2.1.tar.xz

pk:
	git clone ${GIT_URL}/riscv-software-src/riscv-pk.git pk

spike:
	git clone ${GIT_URL}/riscv-software-src/riscv-isa-sim.git spike

Develop Flow
============

### RISC-V

下载仓库和子仓库：

    $ git clone https://github.com/lhtin/riscv-gnu-toolchain.git
    $ cd dev && make clone -j

    或者从GitHub加速网站下载

    $ git clone https://hub.fgit.cf/lhtin/riscv-gnu-toolchain.git
    $ cd dev && make clone -j GIT_URL=https://hub.fgit.cf

    # 如果你有多个功能在同时开发，可以复制dev/gcc
    cp -rf gcc gcc-golden

安装依赖（推荐使用[准备好的Docker环境](https://github.com/lhtin/docker-dev-env/tree/main/dev)，通过ssh登录进行开发）：

    # Ubuntu
    $ sudo yum install autoconf automake autogen python3 libmpc-devel mpfr-devel gmp-devel gawk  bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel ninja-build
    
    # CentOS
    $ sudo yum install autoconf automake python3 libmpc-devel mpfr-devel gmp-devel gawk  bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel

构建调试版本（在dev目录下执行以下命令）：

    $ ./dev-riscv.py --with-arch rv64gc --with-abi lp64d --with-sim qemu --jobs 60

   - will compiling GCC with `-O0 -g3` flags for GDB debug with static linking. `--release` use `-O2`
   - you can specify all options that supported by `./configure` to `./dev-riscv.py`
   - `--help` 展示更多选项
   - `--src-dir` 表示各组件的源代码放的位置，默认为`.`，表示使用当前目录所在的源代码
   - `--gcc-src` 表示GCC源代码在src-dir目录中的名字，默认为gcc，如果你同时有几个GCC在开发，可以通过这个选项区分
   - `--tags` Also generate tags of source code
   - 编译出来的gcc放在`build/debug-gcc-rv64gc-lp64d-medany-linux-qemu/install`下面

运行测试：

    $ cd build/debug-gcc-rv64gc-lp64d-medany-linux-qemu
    $ make report-linux -j60 # 全量测试c, c++, fortran
    或者
    $ make report-linux -j5 RUNTESTFLAGS="riscv.exp=save-restore-9.c" # 运行指定测试
    $ less build-gcc-linux-stage2/gcc/testsuite/gcc/gcc.log # 查看测试详情

重新运行测试需要删除以下文件：

    $ rm stamps/check-gcc-linux

增量编译：

    $ cd build/build/dev-rv64gc-lp64d-medany-linux-qemu-debug/build-gcc-linux-stage2
    $ make -j && make install -j

### GCC仓库更新和提交

GCC update:

    $ cd gcc
    $ git pull origin trunk --rebase
    $ git remote add upstream git://gcc.gnu.org/git/gcc.git
    $ git pull upstream trunk --rebase

GCC push:

    $ cd gcc
    $ git remote add lhtin git+ssh://lhtin@gcc.gnu.org/git/gcc.git # Change lhtin to your account
    $ git push lhtin --verbose

### x64

编译带bootstrap：

    # -gcc-src传入gcc仓库的名字
    $ ./dev-x64.py --gcc-src gcc --bootstrap --jobs 50
    # 构建路径：build/x64-debug-gcc-bootstrap

编译不带bootstrap：

    $ ./dev-x64.py --gcc-src gcc --jobs 50
    # 构建路径：build/x64-debug-gcc-simple

测试：
    
    $ cd build/x64-debug-gcc-bootstrap && make check-gcc -j50
    # 或者构建的时候加上 --test 参数

### AArch64

编译：

    $ ./dev-aarch64.py --gcc-src gcc --jobs 50

测试：

    $ ./dev-aarch64.py --gcc-src gcc --jobs 50 --test



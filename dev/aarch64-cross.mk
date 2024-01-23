ROOT_DIR := $(shell pwd)
SRC_DIR=$(ROOT_DIR)
BINUTILS_SRC_DIR=$(SRC_DIR)/binutils
GCC_SRC_DIR=$(SRC_DIR)/gcc
GLIBC_SRC_DIR=$(SRC_DIR)/glibc
DEJAGNU_SRC_DIR=$(SRC_DIR)/dejagnu
QEMU_SRC_DIR=$(SRC_DIR)/qemu
LINUX_HEADERS_SRC_DIR := $(SRC_DIR)/linux-headers-aarch64/include
TARGET=aarch64-unknown-linux-gnu
# WIDTH_ARCH=armv8.8-a+sve
WIDTH_ARCH=armv9-a

ifndef DATE
	DATE := $(shell date +%Y_%m_%d_%H_%M_%S)
endif

BUILD_DIR=$(ROOT_DIR)/build/build-$(TARGET)-$(DATE)
PREFIX_DIR=$(BUILD_DIR)/install
SYSROOT=$(PREFIX_DIR)/sysroot

SIM_PREPARE=SYSROOT=$(SYSROOT) PATH=$(SRC_DIR)/qemu-wrapper:$(PREFIX_DIR)/bin:$(PATH)

CFLAGS = -O0 -g3
CXXFLAGS = $(CFLAGS)
CFLAGS_FOR_TARGET = -O2
CXXFLAGS_FOR_TARGET = $(CFLAGS_FOR_TARGET)
LDFLAGS=-static

export PATH := $(PREFIX_DIR)/bin:$(PATH)

build: $(BUILD_DIR)/build-gcc-stage2 $(BUILD_DIR)/build-qemu $(BUILD_DIR)/build-dejagnu

prefix:
	mkdir -p $(PREFIX_DIR)
	mkdir -p $(SYSROOT)/usr/
	cp -a $(LINUX_HEADERS_SRC_DIR) $(SYSROOT)/usr/

$(BUILD_DIR)/build-binutils: prefix
	mkdir $@
	cd $@ && $(BINUTILS_SRC_DIR)/configure \
		--target=$(TARGET) \
		--prefix=$(PREFIX_DIR) \
		--with-sysroot=$(SYSROOT) \
		$(MULTILIB) \
		--disable-werror \
		--disable-nls \
		--with-expat=yes  \
		--disable-gdb \
		--disable-sim \
		--disable-libdecnumber \
		--disable-readline \
		--disable-gprofng
	$(MAKE) -C $@ LDFLAGS="--static"
	$(MAKE) -C $@ install

# gcc-stage1
$(BUILD_DIR)/build-gcc-stage1: $(BUILD_DIR)/build-binutils
	mkdir $@
	cd $@ && $(GCC_SRC_DIR)/configure \
		--target=$(TARGET) \
		--prefix=$(PREFIX_DIR) \
		--with-sysroot=$(SYSROOT) \
		--with-newlib \
		--without-headers \
		--disable-shared \
		--disable-threads \
		--with-system-zlib \
		--enable-tls \
		--enable-languages=c \
		--disable-libatomic \
		--disable-libmudflap \
		--disable-libssp \
		--disable-libquadmath \
		--disable-libgomp \
		--disable-nls \
		--disable-bootstrap \
		--src=$(GCC_SRC_DIR) \
		$(MULTILIB) \
		--with-abi=$(WIDTH_ABI) \
		--with-arch=$(WIDTH_ARCH) \
		LDFLAGS="$(LDFLAGS)" \
		CFLAGS="$(CFLAGS)" \
		CXXFLAGS="$(CXXFLAGS)" \
		CFLAGS_FOR_TARGET="$(CFLAGS_FOR_TARGET)" \
		CXXFLAGS_FOR_TARGET="$(CXXFLAGS_FOR_TARGET)"
	$(MAKE) -C $@ inhibit-libc=true all-gcc
	$(MAKE) -C $@ inhibit-libc=true install-gcc
	$(MAKE) -C $@ inhibit-libc=true all-target-libgcc
	$(MAKE) -C $@ inhibit-libc=true install-target-libgcc

$(BUILD_DIR)/build-glibc-headers: $(BUILD_DIR)/build-gcc-stage1
	mkdir $@
	cd $@ && $(GLIBC_SRC_DIR)/configure \
		CC=$(TARGET)-gcc \
		CXX=$(TARGET)-g++ \
		CFLAGS="-O2" \
		CXXFLAGS="-O2" \
		LDFLAGS="" \
		--host=$(TARGET) \
		--prefix=$(SYSROOT)/usr \
		--enable-shared \
		--with-headers=$(LINUX_HEADERS_SRC_DIR) \
		--enable-kernel=3.0.0 \
		$(MULTILIB)
	$(MAKE) -C $@ install-headers

$(BUILD_DIR)/build-glibc: $(BUILD_DIR)/build-gcc-stage1
	mkdir $@
	cd $@ && $(GLIBC_SRC_DIR)/configure \
		CC=$(TARGET)-gcc \
		CXX=$(TARGET)-g++ \
		CFLAGS="-O2" \
		CXXFLAGS="-O2" \
		LDFLAGS="" \
		--host=$(TARGET) \
		--prefix=/usr \
		--disable-werror \
		--enable-shared \
		--enable-obsolete-rpc \
		--with-headers=$(LINUX_HEADERS_SRC_DIR) \
		--enable-kernel=3.0.0 \
		$(MULTILIB) \
		--libdir=/usr/lib libc_cv_slibdir=/lib libc_cv_rtlddir=/lib
	$(MAKE) -C $@
	+flock $(SYSROOT)/.lock $(MAKE) -C $@ install install_root=$(SYSROOT)

# gcc-stage2
$(BUILD_DIR)/build-gcc-stage2: $(BUILD_DIR)/build-glibc $(BUILD_DIR)/build-glibc-headers
	mkdir $@
	cd $@ && $(GCC_SRC_DIR)/configure \
		--target=$(TARGET) \
		--prefix=$(PREFIX_DIR) \
		--with-sysroot=$(SYSROOT) \
		--with-system-zlib \
		--enable-shared \
		--enable-tls \
		--enable-languages=c,c++ \
		--disable-libmudflap \
		--disable-libssp \
		--disable-libquadmath \
		--disable-libsanitizer \
		--disable-nls \
		--disable-bootstrap \
		--src=$(GCC_SRC_DIR) \
		$(MULTILIB) \
		--with-abi=$(WIDTH_ABI) \
		--with-arch=$(WIDTH_ARCH) \
		LDFLAGS="$(LDFLAGS)" \
		CFLAGS="$(CFLAGS)" \
		CXXFLAGS="$(CXXFLAGS)" \
		CFLAGS_FOR_TARGET="$(CFLAGS_FOR_TARGET)" \
		CXXFLAGS_FOR_TARGET="$(CXXFLAGS_FOR_TARGET)"
	$(MAKE) -C $@
	$(MAKE) -C $@ install
	cp -a $(PREFIX_DIR)/$(TARGET)/lib* $(SYSROOT)
	echo "Build Success."

$(BUILD_DIR)/build-dejagnu: prefix
	mkdir $@
	cd $@ && $(DEJAGNU_SRC_DIR)/configure \
	prefix=$(PREFIX_DIR)
	$(MAKE) -C $@
	$(MAKE) -C $@ install

$(BUILD_DIR)/build-qemu: prefix
	mkdir $@
	cd $@ && $(QEMU_SRC_DIR)/configure \
		--prefix=$(PREFIX_DIR) \
		--target-list=aarch64-linux-user \
		--interp-prefix=$(PREFIX_DIR)/sysroot \
		--python=python3 \
		--static
	$(MAKE) -C $@
	$(MAKE) -C $@ install

test:
	$(SIM_PREPARE) $(MAKE) -C $(BUILD_DIR)/build-gcc-stage2 check-gcc RUNTESTFLAGS="--target_board=aarch64-sim-linux"
	#$(SIM_PREPARE) $(MAKE) -C $(BUILD_DIR)/build-gcc-stage2 check-gcc RUNTESTFLAGS="--target_board=aarch64-sim-linux vect.exp=vect-gather-1.c"

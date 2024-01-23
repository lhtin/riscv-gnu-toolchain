ROOT_DIR=$(shell pwd)

ifndef DATE
	DATE=$(shell date +%Y_%m_%d_%H_%M_%S)
endif

GCC_SRC=gcc
GCC_SRC_DIR=$(ROOT_DIR)/$(GCC_SRC)

CFLAGS = -O0 -g3
CXXFLAGS = $(CFLAGS)
CFLAGS_FOR_TARGET = $(CFLAGS)
CXXFLAGS_FOR_TARGET = $(CFLAGS)
LDFLAGS=-static

BUILD_DIR=$(ROOT_DIR)/build/build-native-simple-$(GCC_SRC)-$(DATE)
PREFIX_DIR=$(BUILD_DIR)/install

build-x64-simple: $(BUILD_DIR)/build-native-simple-gcc-stamp

test-x64-simple: $(BUILD_DIR)/build-test-simple-gcc

prefix-x64-simple:
	mkdir -p $(PREFIX_DIR)

# simple x86_64 gcc

$(BUILD_DIR)/build-native-simple-gcc-stamp: prefix-x64-simple
	rm -rf $(BUILD_DIR)/build-gcc
	mkdir $(BUILD_DIR)/build-gcc
	cd $(BUILD_DIR)/build-gcc && $(GCC_SRC_DIR)/configure \
		--prefix=$(PREFIX_DIR) \
		--disable-bootstrap \
		--disable-multilib \
		LDFLAGS="$(LDFLAGS)" \
		CFLAGS="$(CFLAGS)" \
		CXXFLAGS="$(CXXFLAGS)" \
		CFLAGS_FOR_TARGET="$(CFLAGS_FOR_TARGET)" \
		CXXFLAGS_FOR_TARGET="$(CXXFLAGS_FOR_TARGET)"
	$(MAKE) -C $(BUILD_DIR)/build-gcc 2>&1 | tee $(BUILD_DIR)/build.log
	$(MAKE) -C $(BUILD_DIR)/build-gcc install 2>&1 | tee $(BUILD_DIR)/install.log
	echo "Build Success."
	touch $@

$(BUILD_DIR)/build-test-simple-gcc: prefix-x64-simple $(BUILD_DIR)/build-native-simple-gcc-stamp
	cd $(BUILD_DIR)/build-gcc
	-$(MAKE) -C $@ check

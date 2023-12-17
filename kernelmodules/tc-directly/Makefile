KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

obj-m := hello.o

.PHONY: all clean install
all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean

install:
	make -C $(KDIR) M=$(PWD) modules_install

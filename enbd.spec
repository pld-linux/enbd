# TODO:
# - include docs, scripts, more files?
# - better descs
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

#
%define	rel	0.1
Summary:	Enhanced Network Block Device
Summary(pl):	Wzbogacona wersja sieciowego urz±dzenia blokowego
Name:		enbd
Version:	2.4.32
Release:	%{rel}
License:	GPL
Group:		Applications/System
Source0:	ftp://oboe.it.uc3m.es/pub/Programs/%{name}-%{version}.tgz
# Source0-md5:	9e201d20a5666ebc22f832f72a8349a2
URL:		http://www.it.uc3m.es/~ptb/nbd/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Enhanced Network Block Device.

%description -l pl
Wzbogacona wersja sieciowego urz±dzenia blokowego.

%package -n kernel-block-enbd
Summary:	embd kernel module
Summary(pl):	Modu³ j±dra enbd
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel-block-enbd
enbd kernel module.

%description -n kernel-block-enbd -l pl
Modu³ j±dra enbd.

%package -n kernel-smp-block-enbd
Summary:	enbd SMP kernel module
Summary(pl):	Modu³ j±dra SMP enbd
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-block-enbd
enbd SMP kernel module.

%description -n kernel-smp-block-enbd -l pl
Modu³ j±dra SMP enbd.

%prep
%setup -q

%build
%if %{with userspace}
cd nbd
%configure2_13
%{__make} \
	CFLAGS="-I../kernel/linux/include"
cd -
%endif

%if %{with kernel}
cd kernel/linux-2.6.x/drivers/block/enbd
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	cp -a ../../../include o
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		CONFIG_BLK_DEV_ENBD=m \
		CONFIG_BLK_DEV_ENBD_IOCTL=m \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	install -d $cfg
	mv *.ko $cfg
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
cd nbd
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_mandir}/man{5,8}}
install enbd-server enbd-cstatd enbd-sstatd enbd-test $RPM_BUILD_ROOT%{_sbindir}
install *.5 $RPM_BUILD_ROOT%{_mandir}/man5
install *.8 $RPM_BUILD_ROOT%{_mandir}/man8
cd -
%endif

%if %{with kernel}
cd kernel/linux-2.6.x/drivers/block/enbd
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
install %{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc

%if %{with smp} && %{with dist_kernel}
install smp/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-block-enbd
%depmod %{_kernel_ver}

%postun -n kernel-block-enbd
%depmod %{_kernel_ver}

%post -n kernel-smp-block-enbd
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-block-enbd
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/enbd-*
%{_mandir}/man[58]/*
%endif

%if %{with kernel}
%files -n kernel-block-enbd
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-block-enbd
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
%endif

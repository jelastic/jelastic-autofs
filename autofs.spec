#
#
%ifarch sparc i386 i586 i686
%define _lib lib
%endif

%ifarch x86_64 sparc64
%define _lib lib
%endif

%define _libdir /usr/lib

# Use --without systemd in your rpmbuild command or force values to 0 to
# disable them.
%define with_systemd        1

# Use --without libtirpc in your rpmbuild command or force values to 0 to
# disable them.
%define with_libtirpc        %{?_without_libtirpc:        0} %{?!_without_libtirpc:        1}

# Use --without fedfs in your rpmbuild command or force values to 0 to
# disable them.
%define with_fedfs           %{?_without_fedfs:         0} %{?!_without_fedfs: 1}

%define version 5.1.8
%define release 1j
Summary: A tool from automatically mounting and umounting filesystems.
Name: autofs
Version: %{version}
Release: 1j%{?dist}
Epoch: 1
License: GPL
Group: System Environment/Daemons
Source: https://www.kernel.org/pub/linux/daemons/autofs/v5/autofs-%{version}.tar.gz
#Patch0: jelastic-autofs.patch
Patch3: autofs-init.patch
Buildroot: %{_tmppath}/%{name}-tmp
%if %{with_systemd}
BuildRequires: systemd-units
BuildRequires: systemd-devel
%endif
%if %{with_libtirpc}
BuildRequires: libtirpc-devel
%endif
BuildRequires: autoconf, hesiod-devel, openldap-devel, bison, flex, cyrus-sasl-devel, openssl-devel, libxml2-devel
Requires: chkconfig
Requires: /bin/bash sed grep /bin/ps
%if %{with_systemd}
Requires(post): systemd-sysv
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%endif
Obsoletes: autofs-ldap
Summary(de): autofs daemon 
Summary(fr): daemon autofs
Summary(tr): autofs sunucu sereci
Summary(sv): autofs-daemon

%description
autofs is a daemon which automatically mounts filesystems when you use
them, and unmounts them later when you are not using them.  This can
include network filesystems, CD-ROMs, floppies, and so forth.

%prep
%setup -q -n %{name}-%{version}
#%patch0 -p1
%patch3 -p1
echo %{version}-%{release} > .version
%if %{with_systemd}
  %define unitdir %{?_unitdir:/lib/systemd/system}
  %define systemd_configure_arg --with-systemd
%endif
%if %{with_libtirpc}
  %define libtirpc_configure_arg --with-libtirpc
%endif
%if %{with_fedfs}
  %define fedfs_configure_arg --enable-fedfs
%endif

%build
CFLAGS="$RPM_OPT_FLAGS -Wall" \
LDFLAGS="-Wl,-z,now" \
./configure --libdir=%{_libdir} \
	--disable-mount-locking \
	--enable-ignore-busy \
	--enable-force-shutdown \
	%{?systemd_configure_arg:} \
	%{?libtirpc_configure_arg:} \
	%{?fedfs_configure_arg:}
CFLAGS="$RPM_OPT_FLAGS -Wall -I/usr/include/libxml2" LDFLAGS="-Wl,-z,now" make initdir=/etc/rc.d/init.d DONTSTRIP=1

%install
rm -rf $RPM_BUILD_ROOT
%if %{with_systemd}
install -d -m 755 $RPM_BUILD_ROOT%{unitdir}
%else
mkdir -p -m755 $RPM_BUILD_ROOT/etc/rc.d/init.d
%endif
mkdir -p -m755 $RPM_BUILD_ROOT%{_sbindir}
mkdir -p -m755 $RPM_BUILD_ROOT%{_libdir}/autofs
mkdir -p -m755 $RPM_BUILD_ROOT%{_mandir}/{man5,man8}
mkdir -p -m755 $RPM_BUILD_ROOT/etc/sysconfig
mkdir -p -m755 $RPM_BUILD_ROOT/etc/auto.master.d

make install mandir=%{_mandir} initdir=/etc/rc.d/init.d INSTALLROOT=$RPM_BUILD_ROOT
echo make -C redhat
make -C redhat
%if %{with_systemd}
# Configure can get this wrong when the unit files appear under /lib and /usr/lib
find $RPM_BUILD_ROOT -type f -name autofs.service -exec rm -f {} \;
install -m 644 redhat/autofs.service $RPM_BUILD_ROOT%{unitdir}/autofs.service
%define init_file_name %{unitdir}/autofs.service
%else
install -m 755 redhat/autofs.init $RPM_BUILD_ROOT/etc/rc.d/init.d/autofs
%define init_file_name /etc/rc.d/init.d/autofs
%endif
install -m 644 redhat/autofs.conf $RPM_BUILD_ROOT/etc/autofs.conf
install -m 644 redhat/autofs.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/autofs

install -m 644 samples/auto.master $RPM_BUILD_ROOT/etc/auto.master
install -m 644 samples/auto.misc $RPM_BUILD_ROOT/etc/auto.misc
install -m 755 samples/auto.net $RPM_BUILD_ROOT/etc/auto.net
install -m 755 samples/auto.smb $RPM_BUILD_ROOT/etc/auto.smb
install -m 600 samples/autofs_ldap_auth.conf $RPM_BUILD_ROOT/etc/autofs_ldap_auth.conf

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post
ldconfig
%if %{with_systemd}
if [ $1 -eq 1 ]; then
	%{_bindir}/systemctl daemon-reload >/dev/null 2>&1 || :
	# autofs has been approved to be enabled by default
#	%{_bindir}/systemctl enable %{name}.service >/dev/null 2>&1 || :
fi
%else
if [ $1 -eq 1 ]; then
	%{_sbindir}/chkconfig --add autofs
fi
%endif

%preun
%if %{with_systemd}
if [ $1 -eq 0 ] ; then
	%{_bindir}/systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
	%{_bindir}/systemctl stop %{name}.service > /dev/null 2>&1 || :
fi
%else
if [ $1 -eq 0 ] ; then
	%{_sbindir}/service autofs stop > /dev/null 2>&1 || :
	%{_sbindir}/chkconfig --del autofs
fi
%endif

%postun
%if %{with_systemd}
%{_bindir}/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
	# Package upgrade, not removal
	%{_bindir}/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
fi
%else
if [ $1 -ge 1 ] ; then
	%{_sbindir}/service autofs condrestart > /dev/null 2>&1 || :
fi
ldconfig
%endif

#%triggerun -- %{name} < $bla release
## Save the current service runlevel info
## User must manually run systemd-sysv-convert --apply %{name}
## to migrate them to systemd targets
#%{_bindir}/systemd-sysv-convert --save %{name} >/dev/null 2>&1 ||:
#
## Run these because the SysV package being removed won't do them
#%{_sbindir}/chkconfig --del %{name} >/dev/null 2>&1 || :
#%{_bindir}/systemctl try-restart %{name}.service >/dev/null 2>&1 || :

%files
%defattr(-,root,root)
%doc CREDITS CHANGELOG INSTALL COPY* README* samples/ldap* samples/autofs.schema samples/autofs_ldap_auth.conf
%{init_file_name}
%config(noreplace) /etc/auto.master
%config(noreplace) /etc/autofs.conf
%config(noreplace,missingok) /etc/auto.misc
%config(noreplace,missingok) /etc/auto.net
%config(noreplace,missingok) /etc/auto.smb
%config(noreplace) /etc/sysconfig/autofs
%config(noreplace) /etc/autofs_ldap_auth.conf
%{_sbindir}/automount
%if %{with_fedfs}
%{_sbindir}/mount.fedfs
%{_sbindir}/fedfs-map-nfs4
%endif
%dir %{_libdir}/autofs
%{_libdir}/libautofs.so
%{_libdir}/autofs/*
%{_mandir}/*/*
%dir /etc/auto.master.d

%changelog
* Mon Sep 30 2022 Dmytro Tsurko <dmytro.tsurko@virtuozzo.com>
- Update package to version 5.1.7.
- Remove mount check patch

* Tue Oct 30 2018 Ian Kent <raven@themaw.net>
- Update package to version 5.1.5.

* Wed May 24 2017 Ian Kent <raven@themaw.net>
- Update package to version 5.1.3.

* Wed Jun  15 2016 Ian Kent <raven@themaw.net>
- Update package to version 5.1.2.



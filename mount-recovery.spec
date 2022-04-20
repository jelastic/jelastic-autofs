Name: mount-recovery
Version: 1.1
Release: 1
Summary: mount-recovery
License: GPL
Group: System Management
Requires: autofs
autoprov: yes
autoreq: yes
BuildRoot: %{_tmppath}/%{name}-tmp
Source1: 50-mount-recovery.conf
Source2: mount-recovery
Source3: mount-recovery.service
Source4: mount-recovery.timer

%description
mount-recovery package


#%prep

#%build

%install
rm -rf $RPM_BUILD_ROOT
install -d -m 755 $RPM_BUILD_ROOT%{_unitdir}
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/systemd/system/autofs.service.d
install -d -m 755 $RPM_BUILD_ROOT%{_usr}/local/sbin
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/systemd/system/autofs.service.d/50-mount-recovery.conf
install -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_unitdir}/mount-recovery.service
install -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_unitdir}/mount-recovery.timer
install -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_usr}/local/sbin/mount-recovery

%post
if [ $1 -eq 1 ]; then
    %{_bindir}/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%files
%{_sysconfdir}/systemd/system/autofs.service.d/50-mount-recovery.conf
%{_unitdir}/mount-recovery.service
%{_unitdir}/mount-recovery.timer
%{_usr}/local/sbin/mount-recovery

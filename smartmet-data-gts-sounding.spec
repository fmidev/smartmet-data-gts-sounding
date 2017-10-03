%define smartmetroot /smartmet

Name:           smartmet-data-gts-sounding
Version:        17.10.3
Release:        2%{?dist}.fmi
Summary:        SmartMet Data WMO TEMP Format (FM-35)
Group:          System Environment/Base
License:        MIT
URL:            https://github.com/fmidev/smartmet-data-gts-sounding
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch

Requires:	smartmet-qdtools
Requires:	bzip2
Requires:	php


%description
TODO

%prep

%build

%pre

%install
rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
cd $RPM_BUILD_ROOT

mkdir -p .%{smartmetroot}/cnf/cron/{cron.d,cron.hourly}
mkdir -p .%{smartmetroot}/data/incoming/gts/sounding
mkdir -p .%{smartmetroot}/editor/in
mkdir -p .%{smartmetroot}/tmp/data/sounding
mkdir -p .%{smartmetroot}/logs/data
mkdir -p .%{smartmetroot}/run/data/sounding_gts/bin

cat > %{buildroot}%{smartmetroot}/cnf/cron/cron.d/sounding-gts.cron <<EOF
*/20 * * * * /smartmet/run/data/sounding_gts/bin/dosounding.php > /smartmet/logs/data/sounding-gts.log 2>&1
EOF

cat > %{buildroot}%{smartmetroot}/cnf/cron/cron.hourly/clean_data_gts_sounding <<EOF
#!/bin/sh
# Clean TEMP data
cleaner -maxfiles 2 '_sounding.sqd' %{smartmetroot}/data/gts/sounding
cleaner -maxfiles 2 '_sounding.sqd' %{smartmetroot}/editor/in

# Clean incoming TEMP data older than 7 days (7 * 24 * 60 = 10080 min)
find /smartmet/data/incoming/gts/sounding -type f -mmin +10080 -delete
EOF

install -m 755 %_topdir/SOURCES/smartmet-data-gts-sounding/dosounding.php %{buildroot}%{smartmetroot}/run/data/sounding_gts/bin/


%post

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,smartmet,smartmet,-)
%config(noreplace) %{smartmetroot}/cnf/cron/cron.d/sounding-gts.cron
%config(noreplace) %attr(0755,smartmet,smartmet) %{smartmetroot}/cnf/cron/cron.hourly/clean_data_gts_sounding
%attr(2775,smartmet,gts)  %dir %{smartmetroot}/data/incoming/gts/sounding
%{smartmetroot}/*

%changelog
* Tue Oct 3 2017 Mikko Rauhala <mikko.rauhala@fmi.fi> 17.10.3-1.el7.fmi
- Initial version


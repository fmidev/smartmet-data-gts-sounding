%define smartmetroot /smartmet

Name:           smartmet-data-gts-sounding
Version:        26.5.21
Release:        1%{?dist}.fmi
Summary:        SmartMet Data WMO TEMP Format (FM-35/36/37) and BUFR
Group:          System Environment/Base
License:        MIT
URL:            https://github.com/fmidev/smartmet-data-gts-sounding
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch

Requires:	smartmet-qdtools
Requires:	pbzip2
Requires:	php


%description
Reads GTS WMO TEMP (FM-35) sounding bulletins and converts them to
SmartMet querydata for the data server and the editor.

%install
rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
cd $RPM_BUILD_ROOT

mkdir -p .%{smartmetroot}/cnf/cron/{cron.d,cron.hourly}
mkdir -p .%{smartmetroot}/data/incoming/gts/{sounding,sounding-bufr}
mkdir -p .%{smartmetroot}/editor/in
mkdir -p .%{smartmetroot}/tmp/data/sounding
mkdir -p .%{smartmetroot}/logs/data
mkdir -p .%{smartmetroot}/run/data/sounding_gts/bin

cat > %{buildroot}%{smartmetroot}/cnf/cron/cron.d/sounding-gts.cron <<EOF
*/20 * * * * /smartmet/run/data/sounding_gts/bin/dosounding.php > /smartmet/logs/data/sounding-gts.log 2>&1
*/20 * * * * /smartmet/run/data/sounding_gts/bin/dosounding-bufr.sh
EOF

cat > %{buildroot}%{smartmetroot}/cnf/cron/cron.hourly/clean_data_gts_sounding <<EOF
#!/bin/sh
# Clean TEMP data
cleaner -maxfiles 2 '_sounding.sqd' %{smartmetroot}/data/gts/sounding
cleaner -maxfiles 2 '_sounding.sqd' %{smartmetroot}/editor/in

# Clean BUFR sounding data
cleaner -maxfiles 2 '_sounding_bufr.sqd' %{smartmetroot}/data/gts/sounding-bufr
cleaner -maxfiles 2 '_sounding_bufr.sqd' %{smartmetroot}/editor/in

# Clean incoming TEMP and BUFR sounding data older than 7 days (7 * 24 * 60 = 10080 min)
find /smartmet/data/incoming/gts/sounding -type f -mmin +10080 -delete
find /smartmet/data/incoming/gts/sounding-bufr -type f -mmin +10080 -delete
EOF

install -m 755 %_topdir/SOURCES/smartmet-data-gts-sounding/dosounding.php %{buildroot}%{smartmetroot}/run/data/sounding_gts/bin/
install -m 755 %_topdir/SOURCES/smartmet-data-gts-sounding/dosounding-bufr.sh %{buildroot}%{smartmetroot}/run/data/sounding_gts/bin/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,smartmet,smartmet,-)
%config(noreplace) %{smartmetroot}/cnf/cron/cron.d/sounding-gts.cron
%config(noreplace) %attr(0755,smartmet,smartmet) %{smartmetroot}/cnf/cron/cron.hourly/clean_data_gts_sounding
%attr(2775,smartmet,gts)  %dir %{smartmetroot}/data/incoming/gts/sounding
%attr(2775,smartmet,gts)  %dir %{smartmetroot}/data/incoming/gts/sounding-bufr
%{smartmetroot}/*

%changelog
* Thu May 21 2026 Mikko Rauhala <mikko.rauhala@fmi.fi> 26.5.21-1.el9.fmi
- Add BUFR sounding ingestion (dosounding-bufr.sh) alongside the
  existing text TEMP flow, with bufrtoqd --subsets and pbzip2
- Rewrite dosounding.php for safety, correctness, and PHP 8 compat
  (fix indentation-vs-logic bug, escape shell args, replace shell-out
  with PHP native, add error handling, drop deprecated ${var} syntax)
- Compress text TEMP output with pbzip2 too, mirroring the BUFR flow.
  The .sqd goes to the data tree and the .bz2 to the editor inbox.
- Correct WMO heading documentation: IU/// is BUFR; TAC TEMP uses
  US/UK (FM-35), UF/UG (FM-36), UA/UB (FM-37). FM-38 unsupported.
- Tighten spec: real %description, drop empty stanzas, require pbzip2
  (and drop now-unused bzip2 dep)
- Add GitHub Actions workflow that builds RPMs for Rocky 8/9/10
* Tue Oct 3 2017 Mikko Rauhala <mikko.rauhala@fmi.fi> 17.10.3-1.el7.fmi
- Initial version


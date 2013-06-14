%global _hardened_build 1
Name:          zookeeper
Version:       3.4.5
Release:       6%{?dist}
Summary:       A high-performance coordination service for distributed applications
Group:         Development/Libraries
License:       ASL 2.0 and BSD
URL:           http://zookeeper.apache.org/
Source0:       http://www.apache.org/dist/%{name}/stable/%{name}-%{version}.tar.gz
Source1:       %{name}-test-template.pom
Source2:       %{name}-ZooInspector-template.pom
Source3:       %{name}.service
# remove non free clover references
# configure ivy to use system libraries
# disable rat-lib and jdiff support
Patch0:        %{name}-3.4.4-build.patch
# https://issues.apache.org/jira/browse/ZOOKEEPER-1557
Patch1:        https://issues.apache.org/jira/secure/attachment/12548109/ZOOKEEPER-1557.patch
Patch2:        %{name}-3.4.5-zktreeutil-gcc.patch
Patch3:        %{name}-3.4.5-disable-cygwin-detection.patch
Patch4:        %{name}-3.4.5-build-contrib.patch
Patch5:        %{name}-3.4.5-add-PIE-and-RELRO.patch
Patch6:        %{name}-3.4.5-atomic.patch

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: boost-devel
BuildRequires: cppunit-devel
BuildRequires: dos2unix
BuildRequires: doxygen
BuildRequires: graphviz
BuildRequires: java-devel
BuildRequires: java-javadoc
BuildRequires: jpackage-utils
BuildRequires: libtool
BuildRequires: libxml2-devel
BuildRequires: log4cxx-devel
BuildRequires: python-devel

BuildRequires: ant
BuildRequires: ant-junit
BuildRequires: apache-ivy
BuildRequires: checkstyle
BuildRequires: jline
BuildRequires: jtoaster
BuildRequires: junit
BuildRequires: log4j
BuildRequires: mockito
BuildRequires: netty
BuildRequires: slf4j
BuildRequires: xerces-j2
BuildRequires: xml-commons-apis

# BuildRequires: rat-lib
# BuildRequires: apache-rat-tasks
# BuildRequires: apache-commons-collections
# BuildRequires: apache-commons-lang
# BuildRequires: jdiff

%description
ZooKeeper is a centralized service for maintaining configuration information,
naming, providing distributed synchronization, and providing group services.

%package lib
Summary:       Zookeeper C client library
Group:         System Environment/Libraries

%description lib
ZooKeeper C client library for communicating with ZooKeeper Server.

%package lib-devel
Summary:       Development files for the %{name} library
Group:         Development/Libraries
Requires:      %{name}-lib%{?_isa} = %{version}-%{release}

%description lib-devel
Development files for the ZooKeeper C client library.

%package lib-doc
Summary:       Documentation for the %{name} library
Group:         Documentation
BuildArch:     noarch

%description lib-doc
Documentation for the ZooKeeper C client library.

%package java
Group:         Development/Libraries
Summary:       Zookeeper Java client library
# Requires:      felix-framework
# Requires:      felix-osgi-compendium
Requires:      checkstyle
Requires:      jline
Requires:      jtoaster
Requires:      junit
Requires:      log4j
Requires:      mockito
Requires:      netty
Requires:      slf4j

Requires:      java
Requires:      jpackage-utils
BuildArch:     noarch

%description java
This package provides a Java client interface to Zookeeper server.

%package javadoc
Group:         Documentation
Summary:       Javadoc for %{name}
BuildArch:     noarch

%description javadoc
This package contains javadoc for %{name}.

%package -n python-ZooKeeper
Group:         Development/Libraries
Summary:       ZooKeeper python binding library
Requires:      %{name}-lib%{?_isa} = %{version}-%{release}
Provides:      zkpython%{?_isa} = %{version}-%{release}

%description -n python-ZooKeeper
ZooKeeper python binding library

%prep
%setup -q
find -name "*.jar" -delete
find -name "*.class" -delete
find -name "*.cmd" -delete
find -name "*.so*" -delete
find -name "*.dll" -delete

%patch0 -p1
%patch1 -p0
%pom_remove_dep org.vafer:jdeb dist-maven/%{name}-%{version}.pom
# jdiff task deps
%pom_remove_dep jdiff:jdiff dist-maven/%{name}-%{version}.pom
%pom_remove_dep xerces:xerces dist-maven/%{name}-%{version}.pom
# rat-lib task deps
%pom_remove_dep org.apache.rat:apache-rat-tasks dist-maven/%{name}-%{version}.pom
%pom_remove_dep commons-collections:commons-collections dist-maven/%{name}-%{version}.pom
%pom_remove_dep commons-lang:commons-lang dist-maven/%{name}-%{version}.pom

%patch2 -p0
%patch3 -p0
%patch4 -p1
%patch5 -p1
%patch6 -p1

sed -i "s|<packaging>pom</packaging>|<packaging>jar</packaging>|" dist-maven/%{name}-%{version}.pom
sed -i "s|<groupId>checkstyle</groupId>|<groupId>com.puppycrawl.tools</groupId>|" dist-maven/%{name}-%{version}.pom
sed -i "s|<artifactId>mockito-all</artifactId>|<artifactId>mockito-core</artifactId>|" dist-maven/%{name}-%{version}.pom

cp -p %{SOURCE1} dist-maven/%{name}-%{version}-test.pom
cp -p %{SOURCE2} dist-maven/%{name}-%{version}-ZooInspector.pom
sed -i "s|@version@|%{version}|" dist-maven/%{name}-%{version}-test.pom dist-maven/%{name}-%{version}-ZooInspector.pom

iconv -f iso8859-1 -t utf-8 src/c/ChangeLog > src/c/ChangeLog.conv && mv -f src/c/ChangeLog.conv src/c/ChangeLog
sed -i 's/\r//' src/c/ChangeLog

# fix build problem on f18
sed -i 's|<exec executable="hostname" outputproperty="host.name"/>|<!--exec executable="hostname" outputproperty="host.name"/-->|' build.xml
sed -i 's|<attribute name="Built-On" value="${host.name}" />|<attribute name="Built-On" value="${user.name}" />|' build.xml

%build

# ensure that source and target are 1.5
%ant -Dtarget.jdk=1.5 \
     -Djavadoc.link.java=%{_javadocdir}/java \
     -Dant.build.javac.source=1.5 \
     -Dant.build.javac.target=1.5 \
     build-generated jar test-jar javadoc javadoc-dev

(
cd src/contrib
%ant -Dversion=%{version} \
     -Dcontribfilesetincludes="zooinspector/build.xml" \
     -Dant.build.javac.source=1.5 \
     -Dant.build.javac.target=1.5 \
     -Dtarget.jdk=1.5 \
     -DlastRevision=-1 \
     -Divy.jar.exists=true \
     -Divy.initialized=true \
     -Ddest.dir=../../build/zookeeper
)

pushd src/c
rm -rf autom4te.cache
autoreconf -fis

%configure --disable-static --disable-rpath --with-syncapi
# Remove rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%{__make} %{?_smp_mflags}
make doxygen-doc
popd

# Compile zktreeutil
pushd src/contrib/zktreeutil
rm -rf autom4te.cache
autoreconf -if
%configure
%{__make} %{?_smp_mflags}
popd

%if 0
%check
# Execute multi-threaded test suite
mkdir -p build/lib
for jar in jline log4j xerces-j2 xml-commons-apis; do \
ln -sf %{_javadir}/$jar.jar build/lib/$jar.jar; \
done
pushd src/c
%{__make} %{?_smp_mflags} zktest-mt
./zktest-mt
popd
%ifarch i386
# Run core Java test suite against zookeeper
ant -Dversion=%{version} -DlastRevision=-1 test-core-java
%endif
%endif

%install

mkdir -p %{buildroot}%{_javadir}/%{name}
install -pm 644 build/%{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}/%{name}.jar
install -pm 644 build/%{name}-%{version}-test.jar %{buildroot}%{_javadir}/%{name}/%{name}-test.jar
install -pm 644 build/contrib/ZooInspector/%{name}-ZooInspector-%{version}.jar %{buildroot}%{_javadir}/%{name}/%{name}-ZooInspector.jar

mkdir -p %{buildroot}%{_mavenpomdir}
install -pm 644 dist-maven/%{name}-%{version}.pom %{buildroot}%{_mavenpomdir}/JPP.%{name}-%{name}.pom
%add_maven_depmap JPP.%{name}-%{name}.pom %{name}/%{name}.jar
install -pm 644 dist-maven/%{name}-%{version}-test.pom %{buildroot}%{_mavenpomdir}/JPP.%{name}-%{name}-test.pom
%add_maven_depmap JPP.%{name}-%{name}-test.pom %{name}/%{name}-test.jar
install -pm 644 dist-maven/%{name}-%{version}-ZooInspector.pom %{buildroot}%{_mavenpomdir}/JPP.%{name}-%{name}-ZooInspector.pom
%add_maven_depmap JPP.%{name}-%{name}-ZooInspector.pom %{name}/%{name}-ZooInspector.jar

mkdir -p %{buildroot}%{_javadocdir}/%{name}/dev
cp -pr build/docs/api/* %{buildroot}%{_javadocdir}/%{name}/
cp -pr build/docs/dev-api/* %{buildroot}%{_javadocdir}/%{name}/dev/

pushd src/c
%{__make} install DESTDIR=%{buildroot}
# cleanup
rm -f docs/html/*.map
popd

pushd src/contrib/zktreeutil
%{__make} install DESTDIR=%{buildroot}
popd

pushd src/contrib/zkpython
%{__python} src/python/setup.py build --build-base=$PWD/build \
install --root=%{buildroot} ;\
chmod 0755 %{buildroot}%{python_sitearch}/zookeeper.so
popd

find %{buildroot} -name '*.la' -exec rm -f {} ';'

# TODO
# bin/zkCleanup.sh
# bin/zkCli.sh
# bin/zkEnv.sh
# bin/zkServer.sh

%post lib -p /sbin/ldconfig
%postun lib -p /sbin/ldconfig

%files 
%{_bindir}/cli_mt
%{_bindir}/cli_st
%{_bindir}/load_gen
%{_bindir}/zktreeutil
%doc src/c/ChangeLog src/c/LICENSE src/c/NOTICE.txt src/c/README src/contrib/zktreeutil/README.txt

%files lib
%{_libdir}/lib*.so.*
%doc src/c/LICENSE src/c/NOTICE.txt

%files lib-devel
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/*.so
%doc src/c/LICENSE src/c/NOTICE.txt

%files lib-doc
%doc src/c/LICENSE src/c/NOTICE.txt src/c/docs/html/*

%files java
%{_javadir}/%{name}/%{name}.jar
%{_javadir}/%{name}/%{name}-test.jar
%{_javadir}/%{name}/%{name}-ZooInspector.jar
%{_mavenpomdir}/JPP.%{name}-%{name}.pom
%{_mavenpomdir}/JPP.%{name}-%{name}-test.pom
%{_mavenpomdir}/JPP.%{name}-%{name}-ZooInspector.pom
%{_mavendepmapfragdir}/%{name}
%doc CHANGES.txt LICENSE.txt NOTICE.txt README.txt

%files javadoc
%{_javadocdir}/%{name}
%doc LICENSE.txt NOTICE.txt

%files -n python-ZooKeeper
%{python_sitearch}/ZooKeeper-?.?-py%{python_version}.egg-info
%{python_sitearch}/zookeeper.so
%doc LICENSE.txt NOTICE.txt src/contrib/zkpython/README

%changelog
* Fri Jun 14 2013 Dan Horák <dan[at]danny.cz> - 3.4.5-6
- use fetch_and_add from GCC, fixes build on non-x86 arches

* Tue Jun 11 2013  gil cattaneo <puntogil@libero.it> 3.4.5-5
- fixed zookeeper.so non-standard-executable-perm thanks to Björn Esser

* Tue Jun 11 2013  gil cattaneo <puntogil@libero.it> 3.4.5-4
- enabled hardened-builds
- fixed fully versioned dependency in subpackages (lib-devel and python)
- fixed License tag
- moved large documentation in lib-doc subpackage

* Sat Apr 27 2013 gil cattaneo <puntogil@libero.it> 3.4.5-3
- built ZooInspector
- added additional poms files

* Tue Apr 23 2013 gil cattaneo <puntogil@libero.it> 3.4.5-2
- building/packaging of the zookeeper-test.jar thanks to Robert Rati

* Sun Dec 02 2012 gil cattaneo <puntogil@libero.it> 3.4.5-1
- update to 3.4.5

* Tue Oct 30 2012 gil cattaneo <puntogil@libero.it> 3.4.4-3
- fix missing hostname

* Fri Oct 12 2012 gil cattaneo <puntogil@libero.it> 3.4.4-2
- add ant-junit as BR

* Fri Oct 12 2012 gil cattaneo <puntogil@libero.it> 3.4.4-1
- update to 3.4.4

* Fri May 18 2012 gil cattaneo <puntogil@libero.it> 3.4.3-1
- initial rpm
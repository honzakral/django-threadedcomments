%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define name django-threadedcomments
%define shortname threadedcomments
%define version 0.9
%define release 1

Summary:        A simple yet flexible threaded commenting system.
Name:           %{name}
Version:        %{version}
Release:        %{release}
Source0:        %{name}-%{version}.tar.gz
License:        BSD
Group:          Development/Libraries
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix:         %{_prefix}
BuildArch:      noarch
Vendor:         Eric Florenzano <floguy@gmail.com>
Url:            http://code.google.com/p/django-threadedcomments/

BuildRequires:  python-setuptools

Requires:  Django == 1.4.3

%description
threadedcomments is a Django application which allows for the simple creation of a threaded commenting system.
Commenters can reply both to the original item, and reply to other comments as well.
The application is (as of 0.9) built on top of django.contrib.comments,
which allows it to be easily extended by other modules.

%prep
%setup -n %{name}

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}
mkdir -p ${RPM_BUILD_ROOT}%{_docdir}/%{name}

data_dirs="docs %{name}/fixtures %{name}/sql"
for d in ${data_dirs}; do
    cp -R ${d} ${RPM_BUILD_ROOT}%{_datadir}/%{name}
done

dir_to_remove="fixtures sql"
for dir in ${dir_to_remove}
do
    rm -rf ${RPM_BUILD_ROOT}%{python_sitelib}/%{name}/${dir}
done

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_datadir}/%{name}/
%doc README.rst CHANGELOG.txt LICENSE.txt CONTRIBUTORS.txt
%{python_sitelib}/%{shortname}/
%{python_sitelib}/django_%{shortname}*.egg-info

__author__ = 'janos'

"""
Automates the process of creating the Tuxedo RNA Sequence Analysis Pipeline in Ubuntu 12.04 LTS
using Fabric and running under Amazon AWS as an EC2 instance.
"""

base_download_urls = {"samtools": "http://sourceforge.net/projects/samtools/files/samtools/",
                      "bowtie": "http://sourceforge.net/projects/bowtie-bio/files/bowtie/",
                      "bowtie2": "http://sourceforge.net/projects/bowtie-bio/files/bowtie2/",
                      "tophat": "http://tophat.cbcb.umd.edu/downloads/",
                      "eigen": "http://bitbucket.org/eigen/eigen/get/",
                      "cufflinks": "http://cufflinks.cbcb.umd.edu/downloads/"
                      }

import config_version_2014 as config_version
from fabric.api import env, run, sudo

env.user = "ubuntu"
env.key_filename = "mykey.pem" #Change for your private key


def download_and_install_samtools():
    """Samtools - for manipulating SAM and BAM files"""

    base_url = base_download_urls["samtools"]
    version = config_version.versions["samtools"]

    file_name = "samtools-" + version + ".tar.bz2"
    samtools_url = base_url + version + "/" + file_name + "/download"

    try:
        run("mkdir ~/src/")
    except:
        pass

    run("curl -L %s > ~/src/%s" % (samtools_url, file_name))
    run("cd ~/src; tar -xvjf %s" % file_name)
    run("cd ~/src/samtools-%s; make clean; make all" % version)
    run("cd ~/src/samtools-%s/bcftools; make clean; make all" % version)

    #Samstools does not include a Make install :(
    sudo("cp ~/src/samtools-%s/samtools /usr/local/bin/" % version)
    #Copy man file
    sudo("cp ~/src/samtools-%s/samtools.1 /usr/local/share/man/" % version)

    #Copy bcftools
    sudo("cp ~/src/samtools-%s/bcftools/bcftools /usr/local/bin/" % version)

    try:
        run("test -f /usr/local/include/bam/")
    except:
        sudo("mkdir -p /usr/local/include/bam/")

    sudo("cp ~/src/samtools-%s/*.h /usr/local/include/bam/" % version)
    sudo("chmod -R a+r /usr/local/include/bam/")

    sudo("cp ~/src/samtools-%s/libbam.a /usr/local/lib/" % version)
    sudo("chmod a+r /usr/local/lib/libbam.a")


def download_and_install_bowtie():
    """Bowtie1 - short sequence aligner"""
    base_url = base_download_urls["bowtie"]
    version = config_version.versions["bowtie"]
    file_name = "bowtie-%s-src.zip" % version

    bowtie_url = base_url + version + "/" + file_name + "/download"
    run("curl -L %s > ~/src/%s" % (bowtie_url, file_name))
    run("cd ~/src/; unzip %s" % file_name)
    run("cd ~/src/bowtie-%s/;  make" % version)
    bowtie_programs = ["bowtie", "bowtie-build", "bowtie-inspect"]
    for bowtie_program in bowtie_programs:
        sudo("cp ~/src/bowtie-%s/%s /usr/local/bin" % (version, bowtie_program))


def download_and_install_bowtie2():
    """Bowtie2 - 2nd generation short sequence alinger"""
    base_url = base_download_urls["bowtie2"]
    version = config_version.versions["bowtie2"]
    file_name = "bowtie2-%s-source.zip" % version

    bowtie2_url = base_url + version + "/" + file_name + "/download"
    run("curl -L %s > ~/src/%s" % (bowtie2_url, file_name))
    run("cd ~/src/; unzip %s" % file_name)
    run("cd ~/src/bowtie2-%s; make" % version)
    bowtie2_programs = ["bowtie2", "bowtie2-align", "bowtie2-build", "bowtie2-inspect"]
    for bowtie2_program in bowtie2_programs:
        sudo("cp ~/src/bowtie2-%s/%s /usr/local/bin" % (version, bowtie2_program))


def download_and_install_tophat():
    """RNA sequence aligner that takes into account sequence gaps as a result of transcription"""
    base_url = base_download_urls["tophat"]
    version = config_version.versions["tophat"]
    file_name = "tophat-%s.tar.gz" % version

    tophat_url = base_url + file_name
    run("curl -L %s > ~/src/%s" % (tophat_url, file_name))
    run("cd ~/src/; tar -xvzf %s" % file_name)
    run("cd ~/src/tophat-%s; ./configure; make all" % version)
    sudo("cd ~/src/tophat-%s; make install" % version)


def download_and_install_eigen():
    """C++ template library for matrix algebra required by Cufflinks"""
    base_url = base_download_urls["eigen"]
    version = config_version.versions["eigen"]

    file_name_base = "eigen-%s" % version
    run("curl -L %s > ~/src/%s " % (base_url + version + ".tar.bz2", file_name_base + ".tar.bz2"))
    run("cd ~/src/; tar -xvjf %s.tar.bz2" % file_name_base)
    sudo("cd ~/src/eigen-eigen*; cp -r Eigen/ /usr/local/include/")
    sudo("chmod -R a+r /usr/local/include/Eigen/")


def from_subversion_install_boost_library():
    """Boost lib package with Ubuntu 12.04 is not new enough for Cufflinks. So we need to build a more up to date Boost
    library."""

    run("cd ~/src; svn co http://svn.boost.org/svn/boost/trunk boost-trunk")
    #TODO: Remove these catch all
    try:
        run("cd ~/src/boost-trunk;./bootstrap.sh; ./b2")
    except:
        pass

    try:
        sudo("cd ~/src/boost-trunk;./b2 install")
    except:
        pass

    sudo("ldconfig")


def download_and_install_cufflinks():
    base_url = base_download_urls["cufflinks"]
    version = config_version.versions["cufflinks"]
    file_name = "cufflinks-%s.tar.gz" % version

    cufflinks_url = base_url + file_name
    run("curl -L %s > ~/src/%s" % (cufflinks_url, file_name))
    run("cd ~/src/; tar -xvzf %s" % file_name)

    run("cd ~/src/cufflinks-%s/;./configure --with-boost-thread=/usr/local/lib/libboost_thread.so" % version)
    run("cd ~/src/cufflinks-%s/;make" % version)
    sudo("cd ~/src/cufflinks-%s/;make install" % version)


def install_packages():
    sudo("apt-get update")
    sudo("apt-get -y install build-essential")
    sudo("apt-get -y install zlib1g-dev")
    sudo("apt-get -y install libncurses-dev")
    sudo("apt-get -y install unzip")
    sudo("apt-get -y install libboost-dev")
    sudo("apt-get -y install libboost-all-dev")
    sudo("apt-get -y install subversion")


if __name__ == "__main__":
    install_packages()
    download_and_install_samtools()
    download_and_install_bowtie()
    download_and_install_bowtie2()
    download_and_install_tophat()
    download_and_install_eigen()
    from_subversion_install_boost_library()
    download_and_install_cufflinks()
    #TODO: Add Java JDK
    #TODO: Add http://www.usadellab.org/cms/?page=trimmomatic
from setuptools import setup, find_packages

from secret_service.packagedata import Version

setup(
    name="secret_service",
    version=Version.get(),
    packages=find_packages(),
    install_requires=["pycrypto"],
    setup_requires=["pycrypto"],
    scripts=["secret_service/secretservice"],
    description = "A terminal tool to manage key/value pairs and encrypt them to a file",
    license = "Apache-2.0",
    keywords = "encryption dictionary passwords password",
    author="Ben Avrahami"
)
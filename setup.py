from setuptools import setup, find_packages

from server.utils.config_server import PROGRAM, VERSION

DESCRIPTION = "Messenger (server part)"

setup(
    name=PROGRAM,
    version=VERSION,
    license="MIT License",
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    include_package_data=True,
    url="https://github.com/DoctorChe/Python_DataBase_PyQT",
    author="Doctor_Che",
    author_email="duncan.reg@yandex.ru",
    maintainer="Doctor_Che",
    maintainer_email="duncan.reg@yandex.ru",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "server_messenger = server.__main__"
        ]
    }
)

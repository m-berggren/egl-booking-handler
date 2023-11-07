from setuptools import find_packages, setup

setup(
    name="eglhandler",
    version="0.0.10",
    description="Python package to handle EGL bookings in Navis",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    author="MB",
    license="MIT",
    install_requires=[
        "azure-core==1.27.0",       
        "azure-identity==1.13.0",
        "certifi==2023.5.7",
        "cffi==1.15.1",
        "charset-normalizer==3.1.0",
        "colorama==0.4.6",
        "cryptography==41.0.1",
        "EasyProcess==1.1",
        "entrypoint2==1.1",
        "idna==3.4",
        "iniconfig==2.0.0",
        "MouseInfo==0.1.3",
        "msal==1.22.0",
        "msal-extensions==1.0.0",
        "mss==9.0.1",
        "packaging==23.1",
        "Pillow==9.5.0",
        "pluggy==1.0.0",
        "portalocker==2.7.0",
        "PyAutoGUI==0.9.54",
        "pycparser==2.21",
        "PyGetWindow==0.0.9",
        "PyJWT==2.7.0",
        "PyMsgBox==1.0.9",
        "PyMuPDF==1.22.3",
        "pyperclip==1.8.2",
        "PyRect==0.2.0",
        "pyscreenshot==3.1",
        "PyScreeze==0.1.29",
        "pytweening==1.0.7",
        "pyyaml==6.0",
        "pywin32==306",
        "requests==2.31.0",
        "six==1.16.0",
        "tqdm==4.65.0",
        "typing_extensions==4.6.3",
        "urllib3==2.0.2",
        ],
    extras_require={"dev": ["pytest==7.3.1",]},
    python_requires=">=3.10",
)
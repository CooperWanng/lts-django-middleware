from setuptools import setup, find_packages

require = [
    "django>=2.2",
    "pyjwt"
]

setup(
    name="lu_middleware",
    version="1.0.1",
    install_requires=require,
    packages=find_packages(),
    zip_safe=True
)

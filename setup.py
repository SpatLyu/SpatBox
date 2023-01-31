from setuptools import setup
from setuptools import find_packages

setup(
    name="spatbox",
    version="0.1.5",
    description="A Python Library For GeoSpatial Data Proressing And Modeling",
    author="SpatLyu",
    author_email="3180929657@qq.com",
    url= "https://github.com/SpatLyu/SpatBox"
    license="MIT license", 
    packages=find_packages(include=["spatbox", "spatbox.*"]),
    include_package_data=True,
    zip_safe=False,
)

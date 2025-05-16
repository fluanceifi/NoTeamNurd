from setuptools import setup, find_packages


with open('README.md', 'r') as fdesc:
    long_description = fdesc.read()

setup(
    name='facesmoothing',
    version='0.1.3',
    description='Python module for applying face smoothing technique to an image',
    author='Kittipat Phunjanna',
    author_email='kittipat.phunjanna@gmail.com',
    download_url='https://github.com/IngKP/AutomaticFaceSmoothing',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords='image face smooth',
    license='MIT',
    install_requires=['opencv-python == 4.8.1.78'],
    python_requires='>=3.8'
    # extras_require={
    #     'tests': ['pytest == 6.2.*']
    # }
)
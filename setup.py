import setuptools

setuptools.setup(
    name="BvSalud",
    version="0.0.4",
    author="Ankush Rana",
    author_email="ankush.ran13@gmail.com",
    description="Download cientific articles and save into the MongoDB",
    long_description="",
    long_description_content_type="",
    url="https://github.com/ankush13r/BvSalud.git",
    packages=['bvs','data','bvs/data'],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.md', '*.json','*.js','*.py'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

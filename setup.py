from setuptools import setup, find_packages

setup(
    name="habit-tracker",
    version="1.0.0",
    description="A habit tracking application that runs on the command-line.",
    author="Alishba Zehra",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "pytest>=8.3.5"
        "questionary>=2.1.0"
    ],
entry_points={
    "console_scripts": [
        "habit_tracker=cli:main"
        ]
},
python_requires=">3.8"
)
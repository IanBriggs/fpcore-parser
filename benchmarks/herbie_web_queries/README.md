# Herbie Web Queries

These are user generated inputs submitted to the
  [Herbie](https://herbie.uwplse.org/doc/latest/using-web.html) web interface.

The raw JSON files are located here as well as a simple script to translate
  them to FPCore.
To translate all json files in the directory run:

> ./json_to_fpcore.py json

It will print the records that were dropped by the translation script.
The most common offense is using a keyword as a variable.


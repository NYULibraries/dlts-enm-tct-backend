## Testing Dependendencies

Our tests run on Django's built-in test suite, which can be run without any additional dependencies.  However, additional testing tools such as coverage can be useful for development purposes, and those have been included in the separate `requirements-testing.txt` file.  To install those utilities, run

```bash
pip install -r requirements-testing.txt
```

## Running Tests

Running all tests is as simple as typing the following from the root project folder

```bash
python manage.py test
```

To run the tests only for a specific module, add that module's name to the commands:

```bash
python manage.py test otcore.hit
```

## Coverage

Coverage is a testing utility that helps assess what parts of your code have sufficient testing and which parts need better test coverage.  Install from the `testing-requirements.txt` file, and then run your tests instead using this command (again from the project root):

```bash
coverage run --source='.' manage.py test
```

Once the tests have run, you can see the coverage report by typing:

```bash
coverage report
```

or, for a more comprehensive, html-generated coverage report, run:

```bash
coverage html
```

which will place file-by-file html coverage reports in the `htmlcov` folder.

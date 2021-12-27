# Gerapy Playwright Example

## Run

There are two ways to run this example:

### Run with Python

```shell script
pip3 install -r requierments.txt
playwright install
python3 run.py
```

### Run with Docker

```shell script
docker run germey/gerapy-playwright-example
```

If you want to build your own docker image, please remember to set:

```python
GERAPY_PLAYWRIGHT_HEADLESS = True
GERAPY_PLAYWRIGHT_NO_SANDBOX = True (default is True)
```

In your settings.py file.

Otherwise, it won't works well.

# qgis-inaturalist-api

[![Contract Tests](https://github.com/javikalsan/qgis-inaturalist-api/actions/workflows/contract-test.yml/badge.svg)](https://github.com/javikalsan/qgis-inaturalist-api/actions/workflows/contract-test.yml)
[![Unit Tests](https://github.com/javikalsan/qgis-inaturalist-api/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/javikalsan/qgis-inaturalist-api/actions/workflows/unit-tests.yml)


Load biodiversity observations from [iNaturalist](https://www.inaturalist.org/) directly into [QGIS](https://qgis.org/). Filter by species, location, date range, username, or current map extent. Visualize nature observations with metadata including photos, observer info, and Wikipedia links.

This plugin <b>is an independent project</b> and <b>not an official iNaturalist collaboration</b>.

![QGIS iNaturalist API Demo](img/qgis-inaturalist-api-demo.gif)

## Plugin development

### Setup

#### Link the plugin to qgis plugin directory
```bash
ln -s /path/to/qgis-inaturalist-api/ ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inaturalist
```

#### Install dev dependencies

Is recommended a Python virtual environment to install the dependencies

```bash
pip install -r requirements-dev.txt
```

#### Install pre-commit
```bash
pre-commit autoupdate
pre-commit install
```

### Testing

**Execution**
```
python -m unittest tests/*/test_*.py
```

**Automatic test execution on file changes (requires [entr](https://github.com/eradman/entr))**
```bash
find . -name "*.py" -not -path "*/venv/*" | entr -c python -m unittest ./tests/*/test_*.py
```
###

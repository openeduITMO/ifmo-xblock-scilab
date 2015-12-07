# ifmo-mod

## Installation

Add this app to you installed apps:

```python
INSTALLED_APPS = (
    #...
    'ifmo_mod',
)
```

You do not need to add any urls to lms/cms urls.py, they are injected as app is started.

### Prereqs

```bash
sudo apt-get install libxml2-dev libxslt-dev libffi-dev
```
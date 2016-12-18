# Docker Tools

Docker Tool provide easy way to management Docker containers and all artifacts.

## Features

```bash
$ docker-management-tools -h
usage: docker-management-tools [-h] [-r REMOVE [REMOVE ...]] [-cv]

Docker management tools.

optional arguments:
  -h, --help            show this help message and exit
  -r REMOVE [REMOVE ...], --remove REMOVE [REMOVE ...]
                        remove container and all connected artifacts (image,
                        volume and network)
  -cv, --clean-volumes  remove orphaned volumes
```

### Remove container with all connected artifacts

Remove containers using IDs. **Be careful**, with container it remove also connected:
* volumes
* network
* image

```bash
$ docker-management-tools -r containerId [containerId1 ... containerIdX]

// eg:
$ docker-management-tools -r f05a129487d6 37fe8fc02ff6
```

### Remove orphaned volumes

```bash
$ docker-management-tools -cv
```

## Usage

This tool is still under development.

If you want to help feel free to pull request.

## Compile

Using `pyinstaller`:

```bash
pyinstaller main.py -F -n docker-management-tools
```

##Credits

Pawel Grzesiecki - Developer (http://signes.pl/) MIT License

Compiled using [pyinstaller](http://www.pyinstaller.org/)

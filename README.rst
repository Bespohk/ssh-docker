sshdocker
=========

A small convenience command to interactively deal with containers running remotely.

Installation
------------

``pip install sshdocker``

Usage
-----

```
ssh-docker <hostname>
```

This will open up an interactive shell (similar to how Supervisord works) allowing you to directly query / perform actions on the containers on the host.

If you'd like to enable autocomplete in ZSH, you can add the following to your `~/.zshrc` file:

```
eval "$(_SSH_DOCKER_COMPLETE=source_zsh ssh-docker)"
```

By entering `ssh-docker [TAB]` you will be able to cycle through all hostnames in your SSH config file.

![circles-web](https://i.imgur.com/G3UJCSI.png)

[![Discord](https://discordapp.com/api/guilds/748687781605408908/widget.png?style=shield)](https://discord.gg/ShEQgUx)

Table of Contents
==================
- [Table of Contents](#table-of-contents)
  - [What is circles-web?](#what-is-circles-web)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Directory Structure](#directory-structure)
  - [The End](#the-end)

What is circles-web?
------

circles-web is the front-facing appearance of the osu! server protocol, [circles](https://github.com/cmyui/circles)!
Using native async/await syntax written on top of [Quart](https://github.com/pgjones/quart) and
[cmyui's multipurpose library](https://github.com/cmyui/cmyui_pkg), circles-web achieves flexability, cleanliness,
and efficiency not seen in other frontend implementations - all while maintaining the simplicity of Python.

A primary goal of circles-web is to keep our codebase a developer-friendly API, so that
programming remains about the logic and ideas, rather than the code itself.

Varkaria and I are mainly writing this. Varkaria handles the design aspect of the frontend, making it responsive
and snappy for mobile users, while I handle the backend, making sure it's easy to modify in every aspect as well
as well as make it as efficent as possible.

circles-web has come a long way, going from [this](https://github.com/Yo-ru/old-circles-web), to what you see now.
It's in quite the usuable state. We now have a fully implemented session authentication system allowing users
to have a more interpersonal experience, leaderboards supported all mods and modes available within the circles
stack, a automated documentation system featuring markdown support, user profiles featuring every single statistic
a player would need from score UR to rank graphs*, and a admin panel allowing for easy management of the circles instance
and it's users*. If you are curious on how far we have gotten, check out our [projects](https://github.com/circles-osu/circles-web/projects),
you can see what we have done and what we are about to complete.

`* a feature that is in development or coming soon.`


Requirements
------

- Some know-how with Linux (tested on Ubuntu 18.04), Python, and general-programming knowledge.
- MySQL
- NGINX

Setup
------

Setup is relatively simple - these commands should set you right up.

Notes:

- Ubuntu 20.04 is known to have issues with NGINX and osu! for unknown reasons?
- If you have any difficulties setting up circles-web, feel free to join the Discord server at the top of the README, we now have a bit of a community!

```sh
# Install Python >=3.9 and latest version of PIP.
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.9 python3.9-dev python3.9-distutils
wget https://bootstrap.pypa.io/get-pip.py
python3.9 get-pip.py && rm get-pip.py

# Install MySQL and NGINX.
sudo apt install mysql-server nginx

# Clone circles-web from GitHub.
git clone https://github.com/circles-osu/circles-web.git
cd circles-web

# Initialize and update the submodules.
git submodule init && git submodule update

# Install requirements from pip.
python3.9 -m pip install -r ext/requirements.txt

# Add and configure circles-web's NGINX config to your nginx/sites-enabled.
sudo ln -r -s ext/nginx.conf /etc/nginx/sites-enabled/circles-web.conf
sudo nano ext/nginx.conf
sudo nginx -s reload

# Configure circles-web.
cp ext/config.sample.py config.py
nano config.py

# Run circles-web.
python3.9 main.py # Run directly to access debug features for development! (Port 5000)
hypercorn main.py # Please run circles-web with hypercorn when in production! It will improve performance drastically by disabling all of the debug features a developer would need! (Port 8000)
```

Directory Structure
------

    .
    ├── blueprints   # Modular routes such as the API, Frontend, or Admin Panel.
    ├── docs         # Markdown files used in circles-web's documentation system.
    ├── ext          # External files from circles-web's primary operation.
    ├── objects      # Code for representing privileges, global objects, and more.
    ├── static       # Code or content that is not modified or processed by circles-web itself.
    ├── templates    # HTML that contains content that is rendered after the page has loaded.
        ├── admin    # Templated content for the admin panel (/admin).
        ├── settings # Templated content for settings (/settings).
        └ ...         # Templated content for all of circles-web (/).

The End
------

Well know that you know everything, why not check out the original code circles-web was based off of in [this](https://github.com/yo-ru/old-circles-web) dusty old archived repository?

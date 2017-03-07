import argparse
import json

import docker
from termcolor import colored

client = docker.from_env()

"""
Configure Docker program.
"""
parser = argparse.ArgumentParser(description="Docker management tools.")
parser.add_argument("--ip", action="store_true", help="list running containers ip addresses")
parser.add_argument("-r", "--remove",
                    nargs="+",
                    help="remove container and all connected artifacts (image, volumes and networks)")
parser.add_argument("--clean-volumes", action="store_true", help="remove orphaned volumes")

args = parser.parse_args()


class DockerContainer:
    """Docker container class

    Wrapper for docker.Container with additional features and syntactic sugar."""

    def __init__(self, container_info):
        self.container = container_info
        self.attributes = container_info.attrs
        pass

    @property
    def id(self):
        return self.container.id

    @property
    def image_id(self):
        return str(self.attributes["Image"]).split(":")[1]

    @property
    def mounts(self):
        return self.attributes["Mounts"]

    @property
    def mounts_local_ids(self):
        return [mount["Name"] for mount in self.mounts if "Driver" in mount and mount["Driver"] == "local"]

    @property
    def networks(self):
        return self.attributes["NetworkSettings"]["Networks"]

    @property
    def networks_ids(self):
        return [value["NetworkID"] for key, value in self.networks.iteritems() if "NetworkID" in value]

    @property
    def container(self):
        return self.container


def get_container_info(container_id):
    """Collect all information about container."""
    try:
        container = DockerContainer(client.containers.get(container_id))
    except docker.errors.NotFound:
        container = None

    return container


def action_remove_container(container_id):
    """Remove container and all artifacts.
    Remove artifacts like: networks, volumes and image"""

    container_info = get_container_info(container_id)

    if not container_info:
        return None

    to_remove_image = container_info.image_id
    to_remove_volumes = container_info.mounts_local_ids
    to_remove_networks = container_info.networks_ids

    try:
        container_info.container.remove()
        result = colored("DONE", "green")
    except docker.errors.APIError:
        result = colored("ERROR", "red")
    print "{} [container] Remove '{}'".format(result, container_id)

    action_remove_image(to_remove_image)

    for volume_id in to_remove_volumes:
        action_remove_volume(volume_id)

    for network_id in to_remove_networks:
        action_remove_network(network_id)


def action_remove_image(image_id):
    """Remove given Docker Image.
    Catch Docker exception and display correct message."""

    try:
        client.images.remove(image=image_id, noprune=False)
        result = colored("DONE", "green")
    except docker.errors.APIError:
        result = colored("ERROR", "red")
    print "{} [image] Remove '{}'".format(result, image_id)


def action_remove_volume(volume_id):
    """Remove given Docker  Volume.
    Catch Docker exception and display correct message."""

    try:
        client.volumes.get(volume_id).remove()
        result = colored("DONE", "green")
    except docker.errors.APIError:
        result = colored("ERROR", "red")
    print "{} [volume] Remove '{}'".format(result, volume_id)


def action_remove_network(network_id):
    """Remove given Docker Network.
    Catch Docker exception and display correct message."""

    try:
        client.networks.get(network_id).remove()
        result = colored("DONE", "green")
    except docker.errors.APIError:
        result = colored("ERROR", "red")
    print "{} [network] Remove '{}'".format(result, network_id)


def action_list_ip():
    for running_container in client.containers.list():
        if running_container:
            action_get_container_ip(running_container)


def action_get_container_ip(container):
    if isinstance(container, str):
        container = get_container_info(container)

    networks = container.attrs["NetworkSettings"]["Networks"]
    container_name = colored(container.name, "green")
    print "[{}] {}".format(container.short_id, container_name)
    for network in networks:
        print " - {} ({})".format(networks[network]["IPAddress"], network)


if args.remove:
    [action_remove_container(to_remove_id) for to_remove_id in args.remove]

if args.ip:
    action_list_ip()

if args.clean_volumes:
    [action_remove_volume(to_remove_id.id) for to_remove_id in client.volumes.list(filters={"dangling": True})]

import argparse

import docker
from termcolor import colored

client = docker.from_env()

"""
Configure Docker program.
"""
parser = argparse.ArgumentParser(description="Docker management tools.")
parser.add_argument("-r", "--remove",
                    nargs="+",
                    help="remove container and all connected artifacts (image, volume and network)")

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
    to_remove_network = container_info.networks_ids

    try:
        container_info.container.remove()
        result = colored("DONE", "green")
    except docker.errors.APIError:
        result = colored("ERROR", "red")
    print "{} [container] Remove '{}'".format(result, container_id)

    try:
        client.images.remove(image=to_remove_image, noprune=False)
        result = colored("DONE", "green")
    except docker.errors.APIError:
        result = colored("ERROR", "red")
    print "{} [image] Remove '{}'".format(result, to_remove_image)

    for volume_id in to_remove_volumes:
        try:
            client.volumes.get(volume_id).remove()
            result = colored("DONE", "green")
        except docker.errors.APIError:
            result = colored("ERROR", "red")
        print "{} [volume] Remove '{}'".format(result, volume_id)

    for network_id in to_remove_network:
        try:
            client.networks.get(network_id).remove()
            result = colored("DONE", "green")
        except docker.errors.APIError:
            result = colored("ERROR", "red")
        print "{} [network] Remove '{}'".format(result, network_id)


if args.remove:
    [action_remove_container(container_id_to_remove) for container_id_to_remove in args.remove]

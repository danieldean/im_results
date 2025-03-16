#!/usr/bin/python3

#
# rtrtme.py
#
# Copyright (c) 2025 Daniel Dean <dd@danieldean.uk>.
#
# Licensed under The MIT License a copy of which you should have
# received. If not, see:
#
# http://opensource.org/licenses/MIT
#

# API documentation: https://rtrt.me/docs/api/rest

import requests
import json
from datetime import datetime, timezone, timedelta


class APIException(Exception):
    """Simple exception to raise.

    Args:
        Exception (Object): Simple exception to raise.
    """

    pass


class RTRTMePy:
    """A straightforward script to authorise, authenticate and interact with RTRT.me."""

    def __init__(self):
        """Initialise a new instance."""
        self._config = None
        self._session = requests.Session()

    def load_config(self, config_file: str = "rtrtme-config.json") -> None:
        """Load the config from file.

        Args:
            config_file (str, optional): Path of the config file to load. Defaults to "rtrtme-config.json".
        """
        self._config_file = config_file
        with open(self._config_file, "rt") as f:
            self._config = json.loads(f.read())

    def save_config(self, d: dict = None) -> None:
        """Save and optionally update the config to file.

        Args:
            d (dict, optional): Dict to add to the config. Defaults to None.
        """
        if d is not None:
            self._config.update(d)
        with open(self._config_file, "wt") as f:
            f.write(json.dumps(self._config, indent=4))

    def _register(self, quite=False) -> None:
        """Register to get a token for further requests.

        Will only register if a token has not been obtained or is thought to have expired.

        Raises:
            APIException: If the registration fails.
        """

        if (
            self._config["token"] is None
            or self._config["token_expires"] <= datetime.now(timezone.utc).timestamp()
        ):

            params = {
                "appid": self._config["app_id"],
            }

            r = self._session.get(f"{self._config['api_url']}register", params=params)

            if r.status_code == 200:
                data = r.json()
                if "error" in data.keys():
                    raise APIException(
                        f"Registration failed: {json.dumps(data, indent=4)}"
                    )
                else:
                    token_expires = int(
                        (datetime.now(timezone.utc) + timedelta(days=30)).timestamp()
                    )
                    self.save_config(
                        {"token": r.json()["token"], "token_expires": token_expires}
                    )
                    if not quite:
                        print("Successfully registered.")
            else:
                raise APIException(f"Registration failed: HTTP Error {r.status_code}")

        else:
            if not quite:
                print("Registration not required as the token is still valid.")

    def _get(
        self,
        endpoint: str,
        params: dict = dict(),
        max: int = 20,
        quite: bool = False,
        list_endpoint: bool = True,
        use_total: bool = False,
    ) -> list:
        """Make a request to a list or single result endpoint.



        Args:
            endpoint (str): Endpoint including IDs, names, etc.
            params (dict, optional): Optional additional parameters to add. Defaults to dict().
            max (int, optional): Change the page size, max supported is 1000. Defaults to 20.
            quite (bool, optional): Whether to print progress or not. Defaults to False.
            list_endpoint (bool, optional): Whether the endpoint is a list endpoint or not. Defaults to True.
            use_total (bool, optional): Request a total to use in progress messages. Defaults to False.

        Raises:
            APIException: If the request fails or returns an error.

        Returns:
            list: List of pages from the endpoint responses.
        """

        self._register(quite=quite)

        params.update(
            {
                "appid": self._config["app_id"],
                "token": self._config["token"],
            }
        )

        if list:
            params.update(
                {
                    "max": max,
                    "start": 1,  # Start at the beginning
                    "total": (
                        1 if use_total else None
                    ),  # Without this there is no way of knowing how many pages
                    "failonmax": 1,
                }
            )

        pages = list()
        page = 1
        total = None

        while True:

            r = self._session.get(f"{self._config['api_url']}{endpoint}", params=params)

            if r.status_code == 200:
                data = r.json()
                if "error" in data.keys():
                    raise APIException(f"Request failed: {json.dumps(data, indent=4)}")
                elif "list" in data.keys() and list_endpoint:

                    if not total and use_total:
                        total = int(data["info"]["total"]) // max + (
                            int(data["info"]["total"]) % max > 0
                        )

                    if not quite:
                        print(
                            f"Fetched page {page} of {total or 'Unknown'} from '{endpoint}'..."
                        )

                    pages.append(data)

                    if len(data["list"]) < max:
                        break
                    else:
                        params.update({"start": params["start"] + max})
                        page += 1
                elif "list" in data.keys() and not list_endpoint:
                    raise APIException(
                        f"'{endpoint}' returns a list not a single response."
                    )
                else:
                    if not quite:
                        print(f"Fetched data from '{endpoint}'...")
                    return [r.json()]

            else:
                raise APIException(
                    f"Request to '{endpoint}' failed: HTTP Error {r.status_code}"
                )

        return pages

    def get_list(
        self,
        endpoint: str,
        params: dict = dict(),
        max: int = 20,
        quite: bool = False,
        use_total: bool = False,
    ) -> dict:
        """Make a request to a list endpoint.

        Args:
            endpoint (str): Endpoint including IDs, names, etc.
            params (dict, optional): Optional additional parameters to add. Defaults to dict().
            max (int, optional): Change the page size, max supported is 1000. Defaults to 20.
            quite (bool, optional): Whether to print progress or not. Defaults to False.
            list (bool, optional): Whether the endpoint is a list endpoint or not. Defaults to True.
            use_total (bool, optional): Request a total to use in progress messages. Defaults to False.

        Raises:
            APIException: If the request fails or returns an error.

        Returns:
            list: List of pages from the endpoint responses.
        """
        return self._get(
            endpoint,
            params=params,
            max=max,
            quite=quite,
            use_total=use_total,
            list_endpoint=True,
        )

    def get(
        self,
        endpoint: str,
        params: dict = dict(),
        quite: bool = False,
    ) -> dict:
        """Make a request to a singe result endpoint.

        If used on a list endpoint this will return just the first response. Use get_list() if unsure.

        Args:
            endpoint (str): Endpoint including IDs, names, etc.
            params (dict, optional): Optional additional parameters to add. Defaults to dict().
            quite (bool, optional): Whether to print progress or not. Defaults to False.

        Raises:
            APIException: If the request fails or returns an error.

        Returns:
            dict: The endpoint responses.
        """
        return self._get(endpoint, params=params, quite=quite, list_endpoint=False)[0]

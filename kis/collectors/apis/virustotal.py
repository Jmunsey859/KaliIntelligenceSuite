# -*- coding: utf-8 -*-
"""
This module contains functionality to obtain sub-domains via the virustotal.com API.
"""

__author__ = "Lukas Reiter"
__license__ = "GPL v3.0"
__copyright__ = """Copyright 2018 Lukas Reiter

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__version__ = 0.1

import os
import json
from collectors.apis.core import ApiCollectionFailed
from collectors.apis.core import BaseApi
from collectors.core import BaseUtils


class Virustotal(BaseApi):
    """This class collects information from virustotal.com"""

    SOURCE_NAME = "virustotal"

    def __init__(self, **args):
        super().__init__(api_name=Virustotal.SOURCE_NAME,
                         filename_template="virustotal.com_domain_{}",
                         **args)
        self._api_domain_url = self._config.config.get(self._api_name, "api_domain_url")
        self._api_key = self._config.config.get(self._api_name, "api_key")

    def collect_api(self, domain: str, output_directory: str = None) -> None:
        """
        This method collects information from the host.io API
        :param domain: The domain to collect information for
        :param output_directory: The directory where the results are stored
        :return:
        """
        if not output_directory or not os.path.isdir(output_directory):
            raise NotADirectoryError("output directory '{}' does not exist".format(output_directory))
        print("[*] querying virustotal.com API")
        url = self._api_domain_url if self._api_domain_url[-1] != "/" else self._api_domain_url[:-1]
        response = self._get_request_info(api_url=url,
                                          params={"apikey": self._api_key,
                                                  "domain": domain})
        if response.status_code == 200:
            query_results = json.loads(response.content)
            BaseUtils.add_json_results(self._command, query_results)
            self.write_filesystem(query_results=query_results,
                                  item=domain,
                                  output_directory=output_directory)
        elif response.status_code == 204:
            raise ApiCollectionFailed("too many requests ({}) - the rate limit has "
                                      "been exceeded".format(response.status_code))
        elif response.status_code == 400:
            raise ApiCollectionFailed("bad request ({}) - the request was somehow "
                                      "incorrect".format(response.status_code))
        elif response.status_code == 403:
            raise ApiCollectionFailed("forbidden ({}) - not enough privileges to make "
                                      "the request".format(response.status_code))
        elif response.status_code == 404:
            raise ApiCollectionFailed("not found ({}) - the resource could not be found".format(response.status_code))
        else:
            raise ApiCollectionFailed("failed with status code: {}".format(response.status_code))

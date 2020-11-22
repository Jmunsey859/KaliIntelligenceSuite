#!/usr/bin/python3
"""
this file implements all unittests for collector httpmsfrobotstxt
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
import tempfile
from typing import List
from typing import Dict
from unittests.tests.collectors.kali.modules.http.core import BaseKaliHttpCollectorTestCase
from unittests.tests.collectors.core import CollectorProducerTestSuite
from collectors.os.modules.http.httpmsfrobotstxt import CollectorClass as HttpMsfRobotstxtCollector
from database.model import Command
from database.model import CollectorType
from database.model import HttpQuery
from database.model import Path
from database.model import ScopeType


class BaseHttpMsfRobotstxtCollectorTestCase(BaseKaliHttpCollectorTestCase):
    """
    This class implements all unittestss for the given collector
    """
    def __init__(self, test_name: str, **kwargs):
        super().__init__(test_name,
                         collector_name="httpmsfrobotstxt",
                         collector_class=HttpMsfRobotstxtCollector)

    @staticmethod
    def get_command_text_outputs() -> List[str]:
        """
        This method returns example outputs of the respective collectors
        :return:
        """
        return """
[*] Processing /root/.msf4/msfconsole.rc for ERB directives.
resource (/root/.msf4/msfconsole.rc)> spool /root/msf_console.log
[*] Spooling to file /root/msf_console.log...
RHOSTS => 10.10.10.138
PORT => 80
SSL => false
[*] [10.10.10.138] /robots.txt found
[+] Contents of Robots.txt:

# Disallow access to the blog until content is finished.
User-agent: *
Disallow: /writeup/
Allow: /test/
/secret.txt
/?page=admin
[*] Scanned 1 of 1 hosts (100% complete)
[*] Auxiliary module execution completed
""".split(os.linesep)

    @staticmethod
    def get_command_json_outputs() -> List[Dict[str, str]]:
        """
        This method returns example outputs of the respective collectors
        :return:
        """
        return []

    def test_verify_results(self):
        """
        This method checks whether the collector correctly verifies the command output
        :return:
        """
        self.init_db()
        with tempfile.TemporaryDirectory() as temp_dir:
            test_suite = CollectorProducerTestSuite(engine=self._engine,
                                                    arguments={"workspace": self._workspaces[0],
                                                               "output_dir": temp_dir})
            with self._engine.session_scope() as session:
                source = self.create_source(session, source_str=self._collector_name)
                command = self.create_command(session=session,
                                              workspace_str=self._workspaces[0],
                                              command=["changeme", "127.0.0.1"],
                                              collector_name_str=self._collector_name,
                                              collector_name_type=CollectorType.service,
                                              service_port=80,
                                              scope=ScopeType.all,
                                              output_path=temp_dir)
                command.stdout_output = self.get_command_text_outputs()
                test_suite.verify_results(session=session,
                                          arg_parse_module=self._arg_parse_module,
                                          command=command,
                                          source=source,
                                          report_item=self._report_item)
        with self._engine.session_scope() as session:
            results = session.query(Command).count()
            self.assertEqual(1, results)
            results = [item.name for item in session.query(Path).all()]
            results.sort()
            self.assertEqual(4, len(results))
            self.assertListEqual(['/', '/secret.txt', '/test/', '/writeup/'], results)
            results = [item.query for item in session.query(HttpQuery).all()]
            self.assertEqual(1, len(results))
            self.assertEqual("page=admin", results[0])
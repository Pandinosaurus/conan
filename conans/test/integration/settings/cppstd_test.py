import unittest

from conans.paths import CONANFILE
from conans.test.utils.tools import TestClient


class StdCppTest(unittest.TestCase):

    def test_use_wrong_setting_for_compiler(self):
        client = TestClient()

        conanfile = """from conans import ConanFile

class TestConan(ConanFile):
    name = "MyLib"
    version = "0.1"
    settings = "compiler", "cppstd"

"""
        client.save({CONANFILE: conanfile})
        client.run('create . user/testing -s compiler="gcc" '
                   '-s compiler.libcxx="libstdc++11" '
                   '-s compiler.version="4.6" -s cppstd=17', assert_error=True)

        self.assertIn("The specified 'cppstd=17' is not available for 'gcc 4.6'", client.out)
        self.assertIn("Possible values are ['11', '98', 'gnu11', 'gnu98']", client.out)

        client.run('create . user/testing -s compiler="gcc" -s compiler.libcxx="libstdc++11" '
                   '-s compiler.version="6.3" -s cppstd=17')

    def test_gcc_8_std_20(self):
        client = TestClient()

        conanfile = """from conans import ConanFile

class TestConan(ConanFile):
    name = "MyLib"
    version = "0.1"
    settings = "compiler", "cppstd"

"""
        client.save({CONANFILE: conanfile})
        client.run('create . user/testing -s compiler="gcc" '
                   '-s compiler.libcxx="libstdc++11" '
                   '-s compiler.version="8" -s cppstd=20')

    def test_set_default_package_id(self):
        client = TestClient()
        conanfile = """from conans import ConanFile

class TestConan(ConanFile):
    name = "MyLib"
    version = "0.1"
    settings = "compiler", %s

    def build(self):
        self.output.warn("BUILDING!")
"""
        # Without the setting
        client.save({CONANFILE: conanfile % ""})
        client.run('create . user/testing -s compiler="gcc" -s compiler.version="7.1" '
                   '-s compiler.libcxx="libstdc++" '
                   '--build missing')
        self.assertIn("BUILDING!", client.out)

        # Add the setting but with the default value, should not build again
        client.save({CONANFILE: conanfile % '"cppstd"'})  # With the setting
        client.run('create . user/testing -s compiler="gcc" -s compiler.version="7.1" '
                   '-s compiler.libcxx="libstdc++" '
                   '-s cppstd=gnu14 '
                   '--build missing')

        if client.cache.config.revisions_enabled:
            self.assertIn("doesn't belong to the installed recipe revision, removing folder",
                          client.out)
            self.assertIn("BUILDING!", client.out)
        else:
            self.assertNotIn("BUILDING!", client.out)

        # Add the setting but with a non-default value, should build again
        client.save({CONANFILE: conanfile % '"cppstd"'})  # With the setting:
        client.run('create . user/testing -s compiler="gcc" -s compiler.version="7.1" '
                   '-s compiler.libcxx="libstdc++" '
                   '-s cppstd=gnu17 '
                   '--build missing')
        self.assertIn("BUILDING!", client.out)

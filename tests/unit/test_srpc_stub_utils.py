from srpcLib.utils import srpc_stub_util


class TestSrpcStubUtils:
    def test_get_service_name(self):
        path = "tests/test_resources/calc/calc_interface.py"
        expected = "calc"
        service_name = srpc_stub_util.get_service_name(path)
        assert expected == service_name

    def test_get_service_interface_class_name(self):
        path = "tests/test_resources/calc/calc_interface.py"
        expected = "CalcInterface"
        service_interface_class_name = srpc_stub_util.get_service_interface_class_name(
            path
        )
        assert expected == service_interface_class_name

    def test_remove_type_hint_from_param_list(self):
        input = ["a:int", "b:float", "c:str"]
        expected = ["a", "b", "c"]
        result = srpc_stub_util.remove_type_hint_from_param_list(input)
        assert expected == result

    def test_get_service_dir(self):
        path = "tests/test_resources/calc/calc_interface.py"
        expected = "tests/test_resources/calc"
        result = srpc_stub_util.get_service_dir(path)
        assert expected == result

    def test_load_module_from_path(self):
        path = "tests/test_resources/calc/calc_interface.py"
        module = srpc_stub_util.load_module_from_path(path)
        expected = "calc_interface"
        assert expected == module.__name__

    def test_check_file_type_hints_sucess(self):
        """Chek sucess in type hint enforcement"""

        file_path = "tests/test_resources/calc/calc_interface.py"
        passed, msg = srpc_stub_util.check_file_type_hints(file_path)
        assert passed is True and "Passed" == msg

    def test_check_file_type_hints_fail(self):
        """Chek fail in type hint enforcement"""

        file_path = "tests/test_resources/calc/calcinconsistentgen_interface.py."
        passed, msg = srpc_stub_util.check_file_type_hints(file_path)
        assert passed is False and not (msg == "Passed")

    def test_check_file_type_hints_generic_fail(self):
        """Chek fail in type hint of generics(lists, dictionaries,...)"""

        file_path = "tests/test_resources/calc/calcinconsistentegen_interface.py."
        passed, msg = srpc_stub_util.check_file_type_hints(file_path)
        assert passed is False and not (msg == "Passed")

    def test_check_file_type_hints_generic_sucess(self):
        """Chek sucess in type hint of generics(lists, dictionaries,...)"""

        file_path = "tests/test_resources/calc/calcconsistentgen_interface.py"
        passed, msg = srpc_stub_util.check_file_type_hints(file_path)
        assert passed is True and msg == "Passed"

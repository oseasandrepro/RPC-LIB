from srpcLib.stub_generator import srpc_stub_utils


class TestSrpcStubUtils:
    def testBuildParamTupleWithNotEmptyList(self):
        params = ["param1", "param2", "param3"]
        expected = "(param1, param2, param3)"
        result = srpc_stub_utils.build_param_tuple(params)

        assert expected == result

    def testBuildParamTupleWithEmptyList(self):
        params = []
        expected = "()"
        result = srpc_stub_utils.build_param_tuple(params)
        assert expected == result

    def testBuildParamTupleWithOneElement(self):
        params = []
        params.append("param1")
        expected = "(param1,)"
        result = srpc_stub_utils.build_param_tuple(params)
        assert expected == result

    def testload_module_from_path(self):
        path = "tests/test_resources/calc/calc_interface.py"
        module = srpc_stub_utils.load_module_from_path(path)
        assert module.__name__ == "calc_interface"

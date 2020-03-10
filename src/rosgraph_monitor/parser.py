#!/usr/bin/env python

import pprint
from pyparsing import *

# TODO: extract nodes, topics, services, etc from 'result'
# Compute Connections


class ModelParser(object):
    def __init__(self, model, isFile=True):
        # OCB = Open Curly Brackets
        # CCB = Close Curly Brackets
        # ORB = Open Round Brackets
        # CRB = Close Round Brackets
        # SQ = Single Quotes'

        OCB, CCB, ORB, CRB, SQ = map(Suppress, "{}()'")
        name = SQ + Word(printables, excludeChars="{},'") + SQ

        sglQStr = QuotedString("'", multiline=True)
        real = Combine(Word(nums) + '.' + Word(nums))
        values = real | Word(
            nums) | Word(alphas) | sglQStr

        _system = Keyword("RosSystem").suppress()
        _name = CaselessKeyword("name").suppress()
        _component = Keyword("RosComponents").suppress()
        _interface = Keyword("ComponentInterface").suppress()

        # Parameter Def
        _parameters = Keyword("RosParameters").suppress()
        _parameter = Keyword("RosParameter").suppress()
        _ref_parameter = Keyword("RefParameter").suppress()
        _value = Keyword("value").suppress()

        # Subscriber Def
        _subscribers = Keyword("RosSubscribers").suppress()
        _subscriber = Keyword("RosSubscriber").suppress()
        _ref_subscriber = Keyword("RefSubscriber").suppress()

        # Subscriber Def
        _publishers = Keyword("RosPublishers").suppress()
        _publisher = Keyword("RosPublisher").suppress()
        _ref_publisher = Keyword("RefPublisher").suppress()

        # ServiceServers Def
        _services = Keyword("RosSrvServers").suppress()
        _service = Keyword("RosServiceServer").suppress()
        _ref_service = Keyword("RefServer").suppress()

        # ServiceClients Def
        _srv_clients = Keyword("RosSrvClients").suppress()
        _srv_client = Keyword("RosServiceClient").suppress()
        _ref_srv_client = Keyword("RefClient").suppress()

        # ActionServers Def
        _action_servers = Keyword("RosActionServers").suppress()
        _action_server = Keyword("RosActionServer").suppress()
        _ref_server = Keyword("RefServer").suppress()

        # Actio Clients Def
        _action_clients = Keyword("RosActionClients").suppress()
        _action_client = Keyword("RosActionClient").suppress()
        _ref_action_client = Keyword("RefClient").suppress()

        # Topic Connections Def
        _topic_connections = Keyword("TopicConnections").suppress()
        _topic_connection = Keyword("TopicConnection").suppress()
        _from = Keyword("From").suppress()
        _to = Keyword("To").suppress()

        param_val = _value + values("value")
        param_vals = Dict(OneOrMore(Group(sglQuotedString.setParseAction(
            removeQuotes) + nestedExpr('{', '}', content=param_val))))
        param_values = _value + \
            nestedExpr('{', '}', content=delimitedList(
                OCB + param_vals + CCB, delim=','))("params")
        param_list = _value + OCB + delimitedList(values, delim=',') + CCB

        param_list = _value + (OCB + delimitedList(
            (values | (OCB + Group(delimitedList(values, delim=',')) + CCB)), delim=',') + CCB)("values")

        parameter = Group(_parameter + name("param_name") +
                          OCB + _ref_parameter + name("param_path") + (param_val | param_list | param_values) + CCB)
        parameters = (_parameters + OCB +
                      OneOrMore(parameter + Optional(",").suppress()) + CCB)

        subscriber = Group(_subscriber + name("sub_name") +
                           OCB + _ref_subscriber + name("sub_path") + CCB)
        subscribers = (_subscribers + OCB +
                       OneOrMore(subscriber + Optional(",").suppress()) + CCB)

        publisher = Group(_publisher + name("pub_name") +
                          OCB + _ref_publisher + name("pub_path") + CCB)
        publishers = (_publishers + OCB +
                      OneOrMore(publisher + Optional(",").suppress()) + CCB)

        service = Group(_service + name("srv_name") +
                        OCB + _ref_service + name("srv_path") + CCB)
        services = (_services + OCB +
                    OneOrMore(service + Optional(",").suppress()) + CCB)

        srv_client = Group(_srv_client + name("srv_name") +
                           OCB + _ref_srv_client + name("srv_path") + CCB)
        srv_clients = (_srv_clients + OCB +
                       OneOrMore(srv_client + Optional(",").suppress()) + CCB)

        action_server = Group(_action_server + name("action_name") +
                              OCB + _ref_server + name("action_path") + CCB)
        action_servers = (_action_servers + OCB +
                          OneOrMore(action_server + Optional(",").suppress()) + CCB)

        action_client = Group(_action_client + name("action_name") +
                              OCB + _ref_action_client + name("action_path") + CCB)
        action_clients = (_action_clients + OCB +
                          OneOrMore(action_client + Optional(",").suppress()) + CCB)

        topic_connection = Group(_topic_connection + name("topic_name") +
                                 OCB + _from + ORB + name("from") + CRB + _to +
                                 ORB + name("to") + CRB + CCB)

        topic_connections = (_topic_connections + OCB +
                             OneOrMore(topic_connection + Optional(",").suppress()) + CCB)

        interface = Group(
            _interface +
            OCB +
            _name + name("interface_name") +
            Optional(parameters)("parameters") +
            Optional(publishers)("publishers") +
            Optional(subscribers)("subscribers") +
            Optional(services)("services") +
            Optional(srv_clients)("srv_clients") +
            Optional(action_servers)("action_servers") +
            Optional(action_clients)("action_clients") +
            CCB)

        self.rossystem_grammar = _system + \
            OCB + \
            _name + name("system_name") + \
            _component + ORB + \
            OneOrMore(interface + Optional(",").suppress())("interfaces") + \
            CRB + Optional(topic_connections)("topic_connections") + CCB
        self._model = model
        self._isFile = isFile

    def _parse_from_string(self):
        self._result = self.rossystem_grammar.parseString(self._model)

    def _parse_from_file(self):
        self._result = self.rossystem_grammar.parseFile(self._model)

    def parse(self):
        try:
            if self._isFile:
                self._parse_from_file()
            else:
                self._parse_from_string()
        except Exception as e:
            print(e.args)   # Should set a default 'result'?
        return self._result


if __name__ == "__main__":
    import os
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(
        my_path, "../../resources/cob4-25.rossystem")
    print(path)

    parser = ModelParser(path)
    try:
        print(parser.parse().dump())
        # print(parser.parse().interfaces[2].services)
    except Exception as e:
        print(e.args)

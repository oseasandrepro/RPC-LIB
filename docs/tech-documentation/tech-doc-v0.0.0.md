# SRPC Technical Documentation

## Table of contents
- [SRPC Technical Documentation](#srpc-technical-documentation)
  - [Table of contents](#table-of-contents)
  - [1. Introduction \& Concepts](#1-introduction--concepts)
    - [1.1 Wat is RPC](#11-wat-is-rpc)
    - [1.2 The SRPC](#12-the-srpc)
  - [2. High-Level Architecture](#2-high-level-architecture)
    - [2.1 What is a Service in SRPC](#21-what-is-a-service-in-srpc)
    - [2.2 Logical Architecture Diagram](#22-logical-architecture-diagram)
  - [3. The SRPC Protocol](#3-the-srpc-protocol)
    - [3.1 Wire Protocol](#31-wire-protocol)
      - [3.1.1 Server response types](#311-server-response-types)
      - [3.1.2 Protocol diagram](#312-protocol-diagram)
  - [4. Core Compoentes(The Internals)](#4-core-compoentesthe-internals)
    - [4.1 The Serializer](#41-the-serializer)
    - [4.2 Binder / Port Mapper](#42-binder--port-mapper)
      - [4.2.1 Server Binder](#421-server-binder)
      - [4.2.2 Client Binder](#422-client-binder)
    - [4.3 Stubs(The Proxies)](#43-stubsthe-proxies)
      - [4.3.1 Server Stub \& Threading Model](#431-server-stub--threading-model)
      - [4.3.2 Client Stub \& Threading Model](#432-client-stub--threading-model)
  - [5. Tooling \& Ecosystem](#5-tooling--ecosystem)
    - [5.1 Stub Generator](#51-stub-generator)
    - [5.2 Metrics](#52-metrics)
      - [5.2.1 Server-Side Logging](#521-server-side-logging)
      - [5.2.2 The Live Dashboard](#522-the-live-dashboard)



## 1. Introduction & Concepts

### 1.1 Wat is RPC
"In distributed computing, a remote procedure call (RPC) is an action in which a computer program causes a procedure to execute in a different address space of the current process (commonly on another computer on a shared computer network), which is written as if it were a local procedure call, without the programmer explicitly writing the details for the remote interaction. That is, the programmer writes essentially the same code whether the subroutine is local to the executing program, or remote. This is a form of server interaction (caller is client, executor is server), typically implemented via a request–response message passing system.The RPC model implies a level of location transparency, namely that calling procedures are largely the same whether they are local or remote, but usually, they are not identical, so local calls can be distinguished from remote calls. Remote calls are usually orders of magnitude slower and less reliable than local calls, so distinguishing them is important." - [Remote procedure call](https://en.wikipedia.org/wiki/Remote_procedure_call).

**Every modern service mesh is descendent of this ideia - just with better Cryptography and fewer open doors.**

"How it works? First, the caller process sends a call message that includes the procedure parameters to the server process. Then, the caller process waits for a reply message (blocks). Next, a process on the server side, which is dormant until the arrival of the call message, extracts the procedure parameters, computes the results, and sends a reply message. The server waits for the next call message. Finally, a process on the caller receives the reply message, extracts the results of the procedure, and the caller resumes execution.

The Remote Procedure Call Flow figure (Figure 1) illustrates the RPC paradigm." - [RPC Model](https://www.ibm.com/docs/en/aix/7.3.0?topic=call-rpc-model).

Figure 1. Remote Procedure Call Flow

![RPC model](../images/rpc_model.jpg)

### 1.2 The SRPC
SRP uses the RPC ideia, and provide a framework to make easy programmers implement services(set of procedures).
SRPC uses Python as IDL(Interface Definition Language), specifically the [abc module](https://docs.python.org/3/library/abc.html) to define service boundaries.

For those with a knack for language design, the idea is to view the use of [abstract types](https://en.wikipedia.org/wiki/Abstract_type)
as "a language" for specifying protocols or interfaces. As many languages implements this concept, essentialy the challenge to extend
the LIB for others langues is to understand "Sockets", "abstract types" and how each language implement types.
Now the LIB only suport Python language.

In the current stage of the project the technical aim is build a solid, extensibile and esay to refactor fundation.
thinking from the users' perspective - programers - the aim is simplify the implementation of distributed processes while preserving a clean programming abstraction.

Core Design Goals:
- Rapid Prototyping: Minimal setup, and auto-generated network bindings.
- Transparent Abstraction: Remote exceptions should feel like local exceptions to the client.

## 2. High-Level Architecture

### 2.1 What is a Service in SRPC
In SRPC, a "Service" is defined strictly by its directory structure and Python naming conventions.  \
This strictness enables the tooling to automatically generate network bindings.

A valid service(in server side) consists of:
1. The Interface: An abstract class defining the methods.
   - The class name must follow the <ServiceName>Interface pattern with an uppercase first letter (e.g., CalcInterface).
   - The class file name must follow the <ServiceName>_interface with an lowercase first letter (eg., calc_interface.py)

2. The Implementation:
   - A concrete class inheriting from the interface, named <ServiceName> with an uppercase first letter (e.g., Calc).
   - the concrete class file name must follow the <ServiceName>.py with an lowercase first letter(eg., calc.py)

3. The Directory
   - The packge directory containing these files must match the package name(all lowercase) exactly (e.g., calc/).

Look the example below, <em>calc</em> is my service name.

**Server Directory Structure**
```
project/
├─ calc/
│  ├─ __init__.py
│  ├─ calc_interface.py
│  ├─ calc.py
├─ srpc_calc_server_stub.py
├─ server.py
.
.
.
```
**Essentialy a SRPC service is an interface**

### 2.2 Logical Architecture Diagram
![logical architecture diagram.png](../images/logical_architecture_diagram.png)

## 3. The SRPC Protocol

### 3.1 Wire Protocol
Here I describe how SRPC uses the TCP protocol to exchange messages between the client and the server.
> [!IMPORTANT]
> Each procedure call on client side establishes a new connection to the server
>
> SRPC serializes Python strings and tuples into bytes before transmitting them over the network.

In the server side, there is a listner for each registered procedure. Each listner one waits for incomming client connections using ``` accept() ``` method  from [Python's socket module (the low-level networking interface)](https://docs.python.org/3/library/socket.html).

When a client connects, ```accepts()``` return a new socket dedicated to that connection. The server then calls ```recv(1024)``` on this socket to receive the client's request.

The server expects the request to be a tuple in the following format: ```(func_name, parameters)```

where:
-  ```func_name``` is the procedure of the procedure to invoke.
- ```parameters``` is a Python  tuple containing the procedure's arguments.

After deserializing the request, the server invokes the corresponding procedure.  \
If the call succeeds, it returns the following response tuple:  \
```("200", "", result)```

where:
- ```200``` indicates sucess.
- ```""``` represents the absence of an error message.
- ```result```  is the rutn value of the procedure.

If the call fails, it returns a tuple int the following format :  \
```(<error_code>, <error_message>, <exception_class>)```

The response is serialized and sent to the client using the ```sendall(...)``` method from Python's socket module.

The value ```1024``` passed to ```recv(1024)``` is a convenient buffer size.

> [!WARNING]
> recv(1024) does not means "Receive the whole message, up to 1024 bytes."
> it means "Receive at most 1024 bytes that are currently available."

#### 3.1.1 Server response types

**Error**

| error code | error message        | exception class |
|:----------------------------------|:-------------:|---------------:|
|"404"       | "The program cannot support the requested procedure"| "SrpcProcUnvailException"|
|"500"       | ```str(exception)``` | ```type(exception).__name__``` |

**Sucess**
| response code | message        | result |
|:-------------------------------|:-------------:|---------------:|
|"200"          | ""             | is the rutn value of the procedure|

#### 3.1.2 Protocol diagram
![srpc wire protocol](../images/srpc_wire_protocol.png)

## 4. Core Compoentes(The Internals)
### 4.1 The Serializer
The SRPC serializer is a simple class called ```SrpcSerializer(srcp_serializer.py)```, that have two methods,  \
```serialize(self, data)``` and ```deserialize(self, data)``` . Currently they are simple [pickle(Python object serialization)](https://docs.python.org/3/library/pickle.html) wrapers.

```serialize(self, data)``` returns ```pickle.dumps(data)```

and ```deserialize(self, data)``` returns ```pickle.loads(data)```

When I was designing I thought it was a good aproach, so the lib can have an extensible class for serialization.  \
And I can change how do I serialize/deserialize only refatoring the fallowing files:
- ```srpc_serializer_interface.py```
- ```srcp_serializer.py```

> [!NOTE]
> Among other factors, the use of a Python-specific serialization mechanism limits the library's portability,
> as it prevents straightforward interoperability with implementations in other programming languages.

### 4.2 Binder / Port Mapper
"The port mapper program maps RPC program and version numbers to transport-specific port numbers.  \
This program makes dynamic binding of remote programs possible.

This is desirable because the range of reserved port numbers is very small and  \
 the number of potential remote programs is very large.  \
By running only the port mapper on a reserved port, the port numbers of other remote programs  \
can be ascertained by querying the port mapper." - [RFC 1057](https://datatracker.ietf.org/doc/html/rfc1057), APPENDIX A.


#### 4.2.1 Server Binder
In SRPC the Binder is builtin with the service during server stub generation.  \
A Binder is an object that have ```start_binder``` and ```stop``` methods, this is defined in  \
```SrpcServerBinderInterface(srpc_server_binder_interface.py)``` interface. it is implemented in
```SrpcServerBinder(srpc_server_binder.py)``` class.

**Essentialy, in SRPC, the Binder holds and serves a Python dictionary where the key is the procedure name and value is the port number**

In the current version(V0.0.0), by standard, every service is listing in TCP port ```5000``` for two types of requests:
- ```("REGISTER", <func_name>, <port_number>)``
- ```("LOOKUP", None, None)```

The ```REGISTER``` is used to append the pair procedure name and port in the binder dictionary.
So after the call of  ```socket.bind(host, 0)``` It is used sockets, on the server it self, to make a ```REGISTER``` request.  \
look the code below:
```
scoket.bind((self.__host, 0))
port = socket.getsockname()[1]
self.__register_func_in_binder(func_name, port)
```
The ```register_func_in_binder(func_name, port)``` is called for each procedure of the service.

The ```LOOKUP``` is used in client side two get the dictionaly of procedures and ports.

Check below how the class ```SrpcServerBinder``` handle this requests:
```python
def __handle_lookup_request(self, conn):
    try:
        msg = conn.recv(1024)
        request_tuple = self.__serializer.deserialize(msg)
        if request_tuple[0] == "LOOKUP":
            response_tuple = ("200", "", self.__functions)
            self.__total_lookup_request += 1
            self.__logger.info(
                f"Total lookup requests: {self.__total_lookup_request}"
            )
        elif request_tuple[0] == "REGISTER":
            req_function = request_tuple[1]
            port = request_tuple[2]
            self.__functions[req_function] = port
            response_tuple = ("200", "", None)
            self.__logger.info(
                f"Function [{req_function}] registered on port #[{port}]"
            )
        else:
            self.__logger.error(f"Unknown request type: {request_tuple[0]}")
            response_tuple = ("500", "erro simulado", None)
```


>[!NOTE]
>This functionality could be removed.
>Eventualy the project gonna follow the contract-first framework aproach.


#### 4.2.2 Client Binder

### 4.3 Stubs(The Proxies)
#### 4.3.1 Server Stub & Threading Model
#### 4.3.2 Client Stub & Threading Model

## 5. Tooling & Ecosystem
### 5.1 Stub Generator
### 5.2 Metrics
#### 5.2.1 Server-Side Logging
#### 5.2.2 The Live Dashboard

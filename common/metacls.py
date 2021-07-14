import pdb
import types
import dis
from icecream import ic


def disassemble(clsdict, black_list):

    funcs = [a for a in clsdict.values() if isinstance(a, types.FunctionType)]
    instructions = [list(dis.get_instructions(f)) for f in funcs]
    for instr in instructions:
        socket_step_to_call = 0  # кол-во инструкций начиная с 'LOAD_GLOBAL' инструкции для socket
        for i in instr:

            if socket_step_to_call > 0:
                socket_step_to_call += 1
                if i.opname.startswith('CALL_FUNCTION'):
                    if socket_step_to_call <= 2:
                        raise TypeError('Incorrect socket usage')  # вызов socket без параметров
                    else:
                        socket_step_to_call = 0  # вызов socket с параметрами

            if i.opname in ['LOAD_GLOBAL', 'LOAD_METHOD']:
                if i.argval == 'socket':
                    socket_step_to_call += 1
                if i.argval in black_list:
                    raise TypeError('Call method of socket from black list')
    pass


class ClientVerifier(type):
    black_list = ['accept', 'listen']

    def __init__(cls, clsname, bases, clsdict):
        disassemble(clsdict, cls.black_list)
        super().__init__(clsname, bases, clsdict)



class ServerVerifier(type):
    black_list = ['connect']


    def __init__(cls, clsname, bases, clsdict):
        disassemble(clsdict, cls.black_list)
        super().__init__(clsname, bases, clsdict)

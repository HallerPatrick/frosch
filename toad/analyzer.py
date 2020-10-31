from bdb import Bdb

def retrieve_post_mortem_stack_infos(tb):
    b = Bdb()
    stack, i = b.get_stack(None, tb)

    # Get global and local vals
    locals = stack[i][0].f_locals
    globals = stack[i][0].f_globals
    return locals, globals

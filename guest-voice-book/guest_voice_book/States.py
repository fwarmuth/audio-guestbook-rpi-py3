from statemachine import StateMachine, State

class TelefoneState(StateMachine):
    on_hook = State('on hook', initial=True)
    off_hook = State('off hook')
    
    pick_up = on_hook.to(off_hook)
    hang_up = off_hook.to(on_hook)


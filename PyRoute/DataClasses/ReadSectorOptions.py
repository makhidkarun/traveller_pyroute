"""
Created on Apr 04, 2023

@author: CyberiaResurrection
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ReadSectorOptions:
    sectors: list
    pop_code: str = 'scaled'
    ru_calc: str = 'scaled'
    route_reuse: int = 10
    trade_choice: str = 'trade'
    route_btn: int = 13
    mp_threads: int = 1
    debug_flag: bool = False
    fix_pop: bool = False

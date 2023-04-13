from aiosow.routines import routine

from exorde.protocol import is_new_work_available

routine(10)(is_new_work_available)

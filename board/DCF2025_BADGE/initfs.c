#include "py/builtin.h"
#include "py/runtime.h"
#include "py/objstr.h"

// Include the initfs tarball
#include "initfs-tarball.h"

// Present the tarball as a bytes object.
static const mp_obj_str_t initfs_tarball_obj = {
    {&mp_type_bytes},
    0, // hash not valid
    sizeof(initfs_tarball_tar_gz),
    initfs_tarball_tar_gz,
};

static const mp_rom_map_elem_t mp_module_initfs_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_initfs) },
    { MP_ROM_QSTR(MP_QSTR_tarball), MP_ROM_PTR(&initfs_tarball_obj) },
};
static MP_DEFINE_CONST_DICT(mp_module_initfs_globals, mp_module_initfs_globals_table);

const mp_obj_module_t mp_module_initfs = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&mp_module_initfs_globals,
};

MP_REGISTER_MODULE(MP_QSTR_initfs, mp_module_initfs);

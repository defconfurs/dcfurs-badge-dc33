# Create an INTERFACE library for our C module.
add_library(initfs INTERFACE)

# Add our source files to the lib
target_sources(initfs INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/initfs.c
    ${CMAKE_CURRENT_BINARY_DIR}/initfs-tarball.h
)
set_source_files_properties(
    ${CMAKE_CURRENT_BINARY_DIR}/initfs-tarball.h
    PROPERTIES GENERATED TRUE)

# Add the current directory as an include directory.
target_include_directories(initfs INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
)

# Generate the initfs
# TODO: This needs better dependency handling.
add_custom_command(
    COMMENT "Generating initial filesystem image"
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/initfs-tarball.h
    BYPRODUCTS ${CMAKE_CURRENT_BINARY_DIR}/initfs-tarball.tar.gz
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND tar -czvf ${CMAKE_CURRENT_BINARY_DIR}/initfs-tarball.tar.gz -C ${CMAKE_CURRENT_LIST_DIR}/../.. initfs
    COMMAND xxd -i initfs-tarball.tar.gz initfs-tarball.h
)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE initfs)

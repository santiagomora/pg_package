from setuptools import find_packages, setup
from core_cpp_packaging_tools.setup_script import\
    get_install_cmake_headers,\
    get_install_cmake_libs,\
    get_build_cmake_ext,\
    get_module_packaging_configuration,\
    CPPPackageConfiguration
from core_cpp_packaging_tools.extension import\
    CMakeExtension
import os


setup_config: CPPPackageConfiguration = get_module_packaging_configuration('core_pg_migrations')


setup(
    packages=find_packages(),
    ext_modules=[
        CMakeExtension(
            name='libcore_pg_migrations_db',
            src_path=setup_config.SRC_PATH,
            cmake_lists_path=os.path.join(setup_config.PACKAGE_CPP_NAME, 'database', 'lib'),
            so_destination_path=os.path.join('lib',  f'python{setup_config.PYTHON_VERSION}'),
            include_files_path=(
                os.path.join(setup_config.PACKAGE_CPP_NAME, 'database', 'lib', 'include'),
                os.path.join('include', f'python{setup_config.PYTHON_VERSION}')
            ),
            is_package=False
        ),
        CMakeExtension(
            name='database_wrapper',
            src_path=setup_config.SRC_PATH,
            cmake_lists_path=os.path.join(setup_config.PACKAGE_CPP_NAME, 'database', 'module'),
            so_destination_path=os.path.join(setup_config.PACKAGE_NAME, 'database', 'cpp'),
            include_files_path=None,
            is_package=True
        ),
        CMakeExtension(
            name='backend_wrapper',
            src_path=setup_config.SRC_PATH,
            cmake_lists_path=os.path.join(setup_config.PACKAGE_CPP_NAME, 'backend'),
            so_destination_path=os.path.join(setup_config.PACKAGE_NAME, 'backend', 'cpp'),
            include_files_path=(
                os.path.join(setup_config.PACKAGE_CPP_NAME, 'backend', 'include'),
                os.path.join('include', f'python{setup_config.PYTHON_VERSION}')
            ),
            is_package=True
        )
    ],
    cmdclass={
        'build_ext': get_build_cmake_ext(setup_config),
        'install_lib': get_install_cmake_libs(setup_config),
        'install_headers': get_install_cmake_headers(setup_config)
    },
    include_package_data=True
)

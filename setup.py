from setuptools import find_packages, setup

package_name = 'handeye_calibration_snapshot_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kimjungtae',
    maintainer_email='buttontg@naver.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
               'snapshot_node = handeye_calibration_snapshot_pkg.snapshot:main',
        ],
    },
)

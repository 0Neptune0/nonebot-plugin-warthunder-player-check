from setuptools import setup, find_packages

with open('README.md', 'r', encoding="utf-8") as md:
    long_description = md.read()

setup(
    name='nonebot-plugin-warthunder-player-check',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "nonebot2 >= 2.0.0",
        "nonebot_adapter_onebot >= 2.2.3",
        "selenium >= 4.10.0",
        "undetected_chromedriver >= 3.5.0",
        "beautifulsoup4",
        "pillow"
    ],
    url='https://github.com/0Neptune0/nonebot-plugin-warthunder-player-check',
    license='GNU General Public License v3.0',
    python_requires=">=3.8",
    author='00.Neptune.00',
    author_email='neptune.0@qq.com',
    description='nonebot2 plugin'
)

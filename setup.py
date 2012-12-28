from distutils.core import setup


setup(
    name='mozawsdeploy',
    version='0.0.1',
    description='Deploy tools for AWS',
    author='Jeremy Orem',
    author_email='oremj@mozilla.com',
    scripts=['scripts/puppet/puppet_aws_lookup'],
    packages=['mozawsdeploy']
)

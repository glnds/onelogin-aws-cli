"""
Collections of entrypoints
"""
import sys

from onelogin_aws_cli import DEFAULT_CONFIG_PATH, OneloginAWS
from onelogin_aws_cli.argparse import OneLoginAWSArgumentParser
from onelogin_aws_cli.configuration import ConfigurationFile


def _load_config(parser, config_file: ConfigurationFile, args=sys.argv[1:]):
    cli_args = parser.parse_args(args)

    with open(DEFAULT_CONFIG_PATH, 'a+') as fp:
        fp.seek(0, 0)
        config_file.file = fp
        config_file.load()

    if (cli_args.configure or not config_file.is_initialised):
        config_file.initialise(cli_args.config_name)

    config_section = config_file.section(cli_args.config_name)

    if config_section is None:
        sys.exit(
            "Configuration '{}' not defined. "
            "Please run 'onelogin-aws-login -c'".format(
                cli_args.config_name
            )
        )

    return config_section, cli_args


def login(args=sys.argv[1:]):
    """
    Entrypoint for `onelogin-aws-login`
    :param args:
    """

    cfg = ConfigurationFile()
    parser = OneLoginAWSArgumentParser()
    config_section, args = _load_config(parser, cfg, args)

    # Handle legacy `--renewSeconds` option while it is deprecated
    if args.renew_seconds or args.renew_seconds_legacy:
        print("ERROR: --renewSeconds  and --renew-seconds have been "
              "deprecated due to longer AWS STS sessions.")
        print("These options will be removed completely in a future version.")
        sys.exit(1)

    config_section.set_overrides(vars(args))

    api = OneloginAWS(config_section)
    api.save_credentials()

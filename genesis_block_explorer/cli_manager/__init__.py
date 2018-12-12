__version__ = '1.0.0'

if __name__ == '__main__':
    import sys
    import os
    from os.path import dirname, abspath
    dirname = dirname(dirname(dirname(abspath(__file__))))
    blex_dir = os.path.join(dirname, 'genesis_block_explorer')
    blex_cli_man_dir = os.path.join(blex_dir, 'cli_manager')
    if os.path.exists(blex_dir) and os.path.exists(blex_cli_man_dir):
        sys.path.insert(0, dirname)

    from genesis_block_explorer.cli_manager.cli import main
    main()

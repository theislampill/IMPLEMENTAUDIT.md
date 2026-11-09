repo = Path(git(Path.cwd(), "rev-parse", "--path-format=absolute", "--show-toplevel").decode().strip())

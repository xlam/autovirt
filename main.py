import argparse

__version__ = "1.0.0"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str)
    parser.add_argument("config", type=str, default="none")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print("args: ", args)
    action_name = args.action
    action_config = args.config
    if action_name == "repair":
        import autovirt.action.repair as action
    if action_name == "salary":
        import autovirt.action.salary as action
    if action_name == "employee":
        import autovirt.action.employee as action
    if action_name == "innovations":
        import autovirt.action.innovations as action
    action.run(action_config)

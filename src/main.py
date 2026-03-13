from src.bootstrap import bootstrap


def main() -> None:
    bot = bootstrap()
    bot.run()


if __name__ == "__main__":
    main()

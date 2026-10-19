"""Launch The Velvet Table. Use --smoke-test for an offscreen rendering check."""
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="The Velvet Table - a pixel card lounge")
    parser.add_argument("--smoke-test", action="store_true", help="Render each screen offscreen and exit")
    parser.add_argument("--screenshots", default="screenshots", help="Smoke-test image output directory")
    args = parser.parse_args()
    if args.smoke_test:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    try:
        from gui import CardGameApp
    except ModuleNotFoundError as error:
        if error.name != "pygame":
            raise
        raise SystemExit("Install the GUI first: python -m pip install -r requirements.txt") from error
    app = CardGameApp()
    if args.smoke_test:
        app.smoke_test(args.screenshots)
    else:
        app.run()


if __name__ == "__main__":
    main()

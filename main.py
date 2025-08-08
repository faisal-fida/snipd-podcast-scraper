import logging

from config import data_dir
from pipeline import SnipdPipeline


logging.basicConfig(level=logging.INFO)


def main() -> None:
    pipeline = SnipdPipeline(data_dir)
    pipeline.run()


if __name__ == "__main__":
    main()

import logging

from snipd_pipeline.pipeline import SnipdPipeline


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def main() -> None:
    pipeline = SnipdPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()

"""
CLI pipeline runner: identify → generate → train → (optionally) feedback loop.
Run from the backend/ directory:
    python pipeline.py --all
    python pipeline.py --identify
    python pipeline.py --generate
    python pipeline.py --train
    python pipeline.py --loop --iterations 5
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def run_identify():
    from engines.identify import IdentifyEngine
    engine = IdentifyEngine()
    attacks = await engine.run()
    logger.info(f"Identify complete — {len(attacks)} attacks in taxonomy")
    return attacks


def run_generate():
    from engines.generate import GenerateEngine
    engine = GenerateEngine()
    path = engine.run()
    logger.info(f"Generate complete — dataset at {path}")
    return path


def run_train():
    from engines.defend import DefendEngine
    engine = DefendEngine()
    metrics = engine.train()
    logger.info(f"Train complete — metrics: {metrics}")
    return metrics


async def run_loop(iterations: int):
    from engines.defend import DefendEngine
    engine = DefendEngine()
    history = await engine.adversarial_loop(iterations=iterations)
    logger.info(f"Feedback loop complete — {len(history)} iterations")
    return history


async def main():
    parser = argparse.ArgumentParser(description="Karna Kavach pipeline runner")
    parser.add_argument("--all",       action="store_true", help="Run full pipeline")
    parser.add_argument("--identify",  action="store_true", help="Run Identify Engine")
    parser.add_argument("--generate",  action="store_true", help="Run Generate Engine")
    parser.add_argument("--train",     action="store_true", help="Train Defend Engine")
    parser.add_argument("--loop",      action="store_true", help="Run adversarial feedback loop")
    parser.add_argument("--iterations", type=int, default=10, help="Feedback loop iterations")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    if args.all or args.identify:
        await run_identify()
    if args.all or args.generate:
        run_generate()
    if args.all or args.train:
        run_train()
    if args.all or args.loop:
        await run_loop(args.iterations)


if __name__ == "__main__":
    asyncio.run(main())

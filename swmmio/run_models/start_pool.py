from swmmio.run_models import run
from swmmio import Model
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import logging
import os

logger = logging.getLogger(__name__)

def run_swmm_engine(inp_path, force=False):
    m = Model(inp_path)
    if not force and m.rpt_is_valid():
        return {"path": inp_path, "status": "skipped"}
    return run.run_hot_start_sequence(m.inp.path)

def main(inp_paths, cores_left=1, force=False):
    workers = max(1, cpu_count() - cores_left)
    results = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_swmm_engine, p, force): p for p in inp_paths}
        for future in as_completed(futures):
            path = futures[future]
            try:
                result = future.result()
            except Exception as e:
                result = {"path": path, "status": "failed", "error": str(e)}
            results.append(result)
            logger.info(result)
    return results  # caller can inspect or save this

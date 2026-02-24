import subprocess
import os
import shutil
import logging
from swmmio import Model

logger = logging.getLogger(__name__)

def run_simple(inp_path):
    """Run a SWMM model via PySWMM directly (no subprocess wrapper needed)."""
    try:
        from pyswmm import Simulation
        with Simulation(inp_path) as sim:
            sim.execute()
        logger.info(f"Completed: {inp_path}")
        return {"path": inp_path, "status": "success", "error": None}
    except Exception as e:
        logger.error(f"Failed: {inp_path} — {e}")
        return {"path": inp_path, "status": "failed", "error": str(e)}

def run_hot_start_sequence(inp_path):
    """
    Run a 3-phase hot-start sequence without mutating the original .inp.
    Works on a temporary copy to preserve the original.
    """
    import tempfile, pandas as pd
    
    base_dir = os.path.dirname(inp_path)
    name = os.path.splitext(os.path.basename(inp_path))[0]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_inp = os.path.join(tmpdir, os.path.basename(inp_path))
        shutil.copy2(inp_path, tmp_inp)
        model = Model(tmp_inp)

        hotstart1 = os.path.join(tmpdir, name + '_hot1.hsf')
        hotstart2 = os.path.join(tmpdir, name + '_hot2.hsf')

        # Phase 1: ignore rainfall, save hotstart1
        model.inp.options.loc['IGNORE_RAINFALL', 'Value'] = 'YES'
        model.inp.files = pd.DataFrame(
            [f'SAVE HOTSTART "{hotstart1}"'], columns=['[FILES]'])
        model.inp.save()
        result = run_simple(model.inp.path)
        if result["status"] == "failed":
            return result  # abort sequence

        # Phase 2: use hotstart1, save hotstart2
        model.inp.files = pd.DataFrame(
            [f'USE HOTSTART "{hotstart1}"', f'SAVE HOTSTART "{hotstart2}"'],
            columns=['[FILES]'])
        model.inp.save()
        result = run_simple(model.inp.path)
        if result["status"] == "failed":
            return result

        # Phase 3: use hotstart2, restore rainfall
        model.inp.files = pd.DataFrame(
            [f'USE HOTSTART "{hotstart2}"'], columns=['[FILES]'])
        model.inp.options.loc['IGNORE_RAINFALL', 'Value'] = 'NO'
        model.inp.save()
        return run_simple(model.inp.path)

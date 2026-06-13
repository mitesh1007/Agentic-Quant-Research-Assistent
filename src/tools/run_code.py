import subprocess
import sys
import tempfile
import os

def run_code(code: str, save_plot: bool = False) -> str:
    """
    Executes Python code in a subprocess and returns stdout + errors.
    Automatically saves any matplotlib plots to outputs/
    """
    # inject plot-saving code if matplotlib is used
    plot_injection = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
_original_show = plt.show
def _save_and_show():
    import os
    from datetime import datetime
    os.makedirs('outputs', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = f'outputs/plot_{timestamp}.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    print(f'Plot saved to {filepath}')
plt.show = _save_and_show
"""

    full_code = plot_injection + "\n" + code

    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(full_code)
            temp_path = f.name

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        os.unlink(temp_path)

        if result.returncode == 0:
            output = result.stdout.strip()
            return output if output else "Code executed successfully with no output."
        else:
            return f"Error:\n{result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out after 60 seconds."
    except Exception as e:
        return f"Error running code: {str(e)}"
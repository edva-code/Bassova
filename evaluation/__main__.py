"""Run the accuracy benchmark: python -m evaluation

Renders each synthetic case to audio, runs the detection pipeline, and reports
note-level and onset F-measures against the known ground truth.
"""

import os
import tempfile
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from engine.pitch_detection import detect_notes
from evaluation.synth import CASES, render_case
from evaluation.metrics import evaluate


def main():
    work_dir = tempfile.mkdtemp(prefix="bassova_eval_")
    results = []

    for name, bpm, spec in CASES:
        path = os.path.join(work_dir, f"{name}.wav")
        ref_notes = render_case(spec, bpm, path)
        est_notes = detect_notes(path)
        results.append((name, evaluate(ref_notes, est_notes)))

    header = f"{'case':<16}{'noteF':>7}{'prec':>7}{'rec':>7}{'onsetF':>8}{'ref':>5}{'est':>5}"
    print(header)
    print("-" * len(header))

    note_f_values = []
    for name, m in results:
        print(
            f"{name:<16}{m['note_f']:>7.2f}{m['note_precision']:>7.2f}"
            f"{m['note_recall']:>7.2f}{m['onset_f']:>8.2f}"
            f"{m['ref_count']:>5}{m['est_count']:>5}"
        )
        note_f_values.append(m["note_f"])

    print("-" * len(header))
    mean_f = sum(note_f_values) / len(note_f_values)
    print(f"{'mean note F':<16}{mean_f:>7.2f}")


if __name__ == "__main__":
    main()

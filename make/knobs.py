from pathlib import Path

from pySC import generate_SC

yaml_filepath = "./configuration.yaml"
output_dir = Path("./data")
output_dir.mkdir(parents=True, exist_ok=True)

SC = generate_SC(yaml_filepath, seed=1)

tune_knob_data = SC.tuning.tune.create_tune_knobs()
tune_knob_data.save_as(str(output_dir/"tune_knobs.json"))

cm_knob_data = SC.tuning.c_minus.create_c_minus_knobs()
cm_knob_data.save_as(str(output_dir/"c_minus_knobs.json"))

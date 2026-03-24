from pathlib import Path

from pySC import generate_SC

yaml_filepath = "./configuration.yaml"
output_dir = Path("./data")
output_dir.mkdir(parents=True, exist_ok=True)

SC = generate_SC(yaml_filepath, seed=1)

# TRM

SC.tuning.calculate_model_trajectory_response_matrix(n_turns=1, save_as=str(output_dir / "trajectory1.json"))
SC.tuning.calculate_model_trajectory_response_matrix(n_turns=2, save_as=str(output_dir / "trajectory2.json"))

# ORM

SC.tuning.calculate_model_orbit_response_matrix(save_as=str(output_dir / "orbit.json"))

# Partial ORM (standalone correctors)

controls = SC.control_arrays["corr"]
hcorr = [name for name in controls if name.endswith("/B1L")]
vcorr = [name for name in controls if name.endswith("/A1L")]
SC.tuning.HCORR = hcorr
SC.tuning.VCORR = vcorr
SC.tuning.calculate_model_orbit_response_matrix(save_as=str(output_dir / "orbit_partial.json"))

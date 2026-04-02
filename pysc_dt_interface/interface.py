from tango import AttributeProxy, DeviceProxy, Database
import os
import time
import numpy as np
from pathlib import Path


print("TANGO_HOST =", os.environ.get('TANGO_HOST'))
data_folder = Path('./data')
data_folder.mkdir(parents=True, exist_ok=True)

# ===== BPMs =====
HBPM = AttributeProxy('sr/diagnostics/bpm_s/HorPos')
VBPM = AttributeProxy('sr/diagnostics/bpm_s/VerPos')

HTBT = AttributeProxy('sr/diagnostics/bpm_s/HorPosTbT')
VTBT = AttributeProxy('sr/diagnostics/bpm_s/VerPosTbT')

TBT_mode = AttributeProxy('sr/diagnostics/bpm_s/TbtMode')
TBT_buffer_size = None


# ===== Get all magnet devices =====
db = Database()
devices = db.get_device_exported("sr/magnet/*").value_string

# ===== Initialize groups =====
hst_names, vst_names, sext_names, quad_names, oct_names, antibend_names = [], [], [], [], [], []

# ===== Classify magnets =====
for dev in devices:
    name = dev.split("/")[-1]

    if name.startswith("ch_"):
        hst_names.append(name)

    elif name.startswith("cv_"):
        vst_names.append(name)

    elif name.startswith(("sf_", "sd_", "sh_")):
        sext_names.append(name)

    elif name.startswith(("qf_", "qd_")):
        quad_names.append(name)

    elif name.startswith("oct_"):
        oct_names.append(name)

    elif name.startswith("qab_"):
        antibend_names.append(name)

# ===== Sort =====
hst_names.sort()
vst_names.sort()
sext_names.sort()
quad_names.sort()
oct_names.sort()
antibend_names.sort()


class Interface:
    wait_after_set = 3.0
    quad_wait_time = 5
    rf_wait_time = 5
    orbit_wait_time = 1.01

    # ===== Reference orbit (DT → zero) =====
    def get_ref_orbit(self):
        bpm_h = HBPM.read().value
        bpm_v = VBPM.read().value

        return np.zeros_like(bpm_h), np.zeros_like(bpm_v)

    # ===== Orbit =====
    def get_orbit(self):
        time.sleep(self.orbit_wait_time)
        return HBPM.read().value, VBPM.read().value

    # ===== Get magnet =====
    def get(self, name: str) -> float:
        try:
            dev = DeviceProxy(f"sr/magnet/{name}")
            return dev.read_attribute("Strength").value
        except Exception as e:
            raise RuntimeError(f"Failed to read {name}: {e}")

    def set(self, name: str, value: float):
        try:
            dev = DeviceProxy(f"sr/magnet/{name}")

            dev.write_attribute("Strength", value)

            if name.startswith(("qf_", "qd_")):
                time.sleep(max(self.quad_wait_time, self.wait_after_set))
            else:
                time.sleep(self.wait_after_set)

        except Exception as e:
            raise RuntimeError(f"Failed to write {name}: {e}")
        
    def get_many(self, names: list[str]) -> dict[str, float]:
        data = {}

        for name in names:
            try:
                dev = DeviceProxy(f"sr/magnet/{name}")

                if name.startswith(("ch_", "cv_")):
                    val = dev.read_attribute("Strength").value
                else:
                    val = dev.read_attribute("CorrectionStrength").value ##it shouldn't be Strength??

                data[name] = val

            except Exception as e:
                raise RuntimeError(f"Failed to read {name}: {e}")

        return data

    def set_many(self, data: dict[str, float]):
        wait_time = self.wait_after_set
        quad_involved = False

        for name, value in data.items():
            try:
                dev = DeviceProxy(f"sr/magnet/{name}")

                if name.startswith(("ch_", "cv_")):
                    dev.write_attribute("Strength", value)
                else:
                    dev.write_attribute("CorrectionStrength", value)

                if name.startswith(("qf_", "qd_")):
                    quad_involved = True

            except Exception as e:
                raise RuntimeError(f"Failed to write {name}: {e}")

        if quad_involved:
            wait_time = max(wait_time, self.quad_wait_time)

        time.sleep(wait_time)

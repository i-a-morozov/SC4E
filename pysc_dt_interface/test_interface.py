from interface import Interface, hst_names, sext_names
import numpy as np
import matplotlib.pyplot as plt
from tango import DeviceProxy


# =========================
# Orbit test
# =========================
def test_orbit():
    ebs = Interface()

    x_ref, y_ref = ebs.get_ref_orbit()
    x, y = ebs.get_orbit()

    bpm_idx = np.arange(1, len(x) + 1)

    print("Number of BPMs:", len(x))
    print("First 5 x_ref:", x_ref[:5])
    print("First 5 y_ref:", y_ref[:5])
    print("First 5 x:", x[:5])
    print("First 5 y:", y[:5])

    plt.figure(figsize=(10, 5))
    plt.plot(bpm_idx, x_ref, label="Ref orbit H")
    plt.plot(bpm_idx, x, "--", label="Orbit H")
    plt.legend()
    plt.grid(True)
    plt.title("Horizontal Orbit")
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(bpm_idx, y_ref, label="Ref orbit V")
    plt.plot(bpm_idx, y, "--", label="Orbit V")
    plt.legend()
    plt.grid(True)
    plt.title("Vertical Orbit")
    plt.show()


# =========================
# Single magnet test
# =========================
def test_single_magnet():
    ebs = Interface()

    test_name = hst_names[0]
    print(f"\nTesting magnet: {test_name}")

    dev = DeviceProxy(f"sr/magnet/{test_name}")

    k0 = ebs.get(test_name)
    k0_str = dev.read_attribute("Strength").value

    print("Initial (interface):", k0)
    print("Initial (Strength):", k0_str)

    dkick = 1e-4
    print("Applying delta:", dkick)

    ebs.set(test_name, k0 + dkick)

    k1 = ebs.get(test_name)
    k1_str = dev.read_attribute("Strength").value

    print("New (interface):", k1)
    print("New (Strength):", k1_str)

    print("Restoring original value...")
    ebs.set(test_name, k0)

    k2 = ebs.get(test_name)
    k2_str = dev.read_attribute("Strength").value

    print("Restored (interface):", k2)
    print("Restored (Strength):", k2_str)


# =========================
# get_many / set_many test
# =========================
def test_many():
    ebs = Interface()

    test_names = sext_names[:2]

    print("\n=== Testing get_many / set_many ===")
    print("Magnets:", test_names)

    devs = {name: DeviceProxy(f"sr/magnet/{name}") for name in test_names}

    data0 = ebs.get_many(test_names)
    data0_str = {n: devs[n].read_attribute("Strength").value for n in test_names}
    data0_corr = {n: devs[n].read_attribute("CorrectionStrength").value for n in test_names}

    print("\nInitial (interface):", data0)
    print("Initial (Strength):", data0_str)
    print("Initial (CorrectionStrength):", data0_corr)

    dk = 1e-3
    new_data = {k: v + dk for k, v in data0.items()}

    print("\nApplying delta:", dk)
    ebs.set_many(new_data)

    data1 = ebs.get_many(test_names)
    data1_str = {n: devs[n].read_attribute("Strength").value for n in test_names}
    data1_corr = {n: devs[n].read_attribute("CorrectionStrength").value for n in test_names}

    print("\nAfter set_many (interface):", data1)
    print("After set_many (Strength):", data1_str)
    print("After set_many (CorrectionStrength):", data1_corr)

    print("\nRestoring original values...")
    ebs.set_many(data0)

    data2 = ebs.get_many(test_names)
    data2_str = {n: devs[n].read_attribute("Strength").value for n in test_names}

    print("\nRestored (interface):", data2)
    print("Restored (Strength):", data2_str)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("\n===== RUNNING INTERFACE TESTS =====\n")

    test_orbit()
    test_single_magnet()
    test_many()

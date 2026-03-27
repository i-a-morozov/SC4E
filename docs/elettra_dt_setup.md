## 1. Connect to the Digital Twin

Connect to the Elettra Digital Twin host using SSH:

    ssh -Y <username>@pcl-ctrl-virt-03.elettra.trieste.it

Use your Elettra LDAP credentials.

After login, you should see a prompt like:

    <username>@pcl-ctrl-virt-03:~$

This confirms that you are connected to the Digital Twin host.

## 2. Configure the Digital Twin Environment
On the Digital Twin host, configure your shell environment by updating your `~/.bashrc`.
Add the following block at the end of the file:

    HOST=$(hostname)

    if [[ "$HOST" == "pcl-ctrl-virt-03" ]]; then
        export TANGO_HOST=srv-tango-ctrl-03:20000
        export LD_LIBRARY_PATH=/usr/local/tango-10.1.1/lib:/usr/local/qwt-6.3.0/lib:/runtime/lib
        export PKG_CONFIG_PATH=/usr/local/tango-10.1.1/lib/pkgconfig:/usr/local/qwt-6.3.0/lib/pkgconfig:/runtime/lib/pkgconfig
        export PATH=/runtime/bin:$PATH
        export PATH=$PATH:/usr/local/tango-10.1.1/bin
        export CUMBIA_INSTALL_ROOT=/runtime
        export QT_PLUGIN_PATH=/runtime/lib/qumbia-plugins
        export PYTHONPATH=/usr/local/lib/python3.13/site-packages:$CUMBIA_INSTALL_ROOT/lib/python3.13/site-packages

        alias qmake='qmake6'
        alias designer='designer6'
    fi

After editing the file, reload the configuration:

    source ~/.bashrc

To verify the setup, check:

    echo $TANGO_HOST

It should return:

    srv-tango-ctrl-03:20000

## 3. Ensure the Digital Twin is Running

Before running pySC, make sure the Digital Twin is running.

### Option 1 — Using Python (recommended)

Run:

    python3

Then:

    import tango
    dev = tango.DeviceProxy("sr/diagnostics/bpm_s")
    print(dev.get_attribute_list())

If this returns a list of attributes, the Digital Twin is running.

---

### Option 2 — Using Astor (optional)

Start Astor:

    astor

In the Astor GUI:

- Locate the **Elettra 2.0 Digital Twin** group
- Check that all servers are in the **ON (green)** state

If servers are OFF, they must be started before using pySC.

## 4. Create and Activate a Python Virtual Environment

To run pySC safely, create a dedicated Python virtual environment on the Digital Twin host.

Create the virtual environment:

    python3 -m venv ~/pysc_env

Activate it:

    source ~/pysc_env/bin/activate

After activation, your shell prompt should look like:

    (pysc_env) <username>@pcl-ctrl-virt-03:~$

---

### Make PyTango Available Inside the Environment

PyTango is installed in the system Python and must be made visible inside the virtual environment.

Run:

    export PYTHONPATH=/usr/local/lib/python3.13/site-packages:$PYTHONPATH

To make this automatic, you can add the same line to:

    ~/pysc_env/bin/activate

## 5. Install pySC

Clone the pySC repository on the Digital Twin host:

    git clone https://github.com/kparasch/pySC.git

Move into the repository:

    cd pySC

Make sure your virtual environment is activated:

    source ~/pysc_env/bin/activate

Install pySC in editable mode:

    pip install -e .

---

### Notes on Dependencies

During installation, you may see warnings related to PyTango dependencies such as:

    docstring_parser
    psutil

These warnings do not prevent pySC from working.

If desired, you can install them with:

    pip install docstring_parser psutil
## 6. Test the Installation

After installing pySC, verify that both PyTango and pySC are working correctly.

Make sure your virtual environment is activated:

    source ~/pysc_env/bin/activate

Start Python:

    python3

Then run:

    import tango
    from pySC import generate_SC

If no errors are raised, the setup is correct.

---

### Optional: Test Access to the Digital Twin

You can also verify that pySC can access the Digital Twin BPM system:

    import tango
    dev = tango.DeviceProxy("sr/diagnostics/bpm_s")
    print(dev.get_attribute_list())

If a list of attributes is returned, the connection to the Digital Twin is working.
